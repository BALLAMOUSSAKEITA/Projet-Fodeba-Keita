from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.eleve import Eleve, Inscription, StatutEleve
from app.models.parametrage import AnneeScolaire, Classe, Niveau, TypeFrais
from app.models.paiements import (
    ModePaiement,
    Paiement,
    RelanceImpaye,
    RemiseEleve,
    SequenceRecu,
    StatutPaiement,
    TarifNiveau,
    TrancheFrais,
)
from app.schemas.paiements import (
    CaisseJournaliereResponse,
    ImpayeItem,
    LigneSituation,
    PaiementAnnulation,
    PaiementCreate,
    PaiementRemboursement,
    PaiementResponse,
    RelanceCreate,
    RemiseEleveCreate,
    SituationEleveResponse,
    TarifNiveauCreate,
    TrancheFraisCreate,
    TrancheSituation,
)
from app.services import parametrage_service, pdf_service


async def _get_eleve_niveau(db: AsyncSession, eleve_id: UUID, annee_id: UUID) -> UUID:
    result = await db.execute(
        select(Inscription.niveau_id).where(
            Inscription.eleve_id == eleve_id,
            Inscription.annee_scolaire_id == annee_id,
            Inscription.statut == StatutEleve.ACTIF.value,
        )
    )
    niveau_id = result.scalar_one_or_none()
    if niveau_id is None:
        raise HTTPException(status_code=404, detail="Inscription introuvable pour cet élève")
    return niveau_id


async def _next_numero_recu(db: AsyncSession, annee_id: UUID) -> str:
    result = await db.execute(
        select(SequenceRecu).where(SequenceRecu.annee_scolaire_id == annee_id)
    )
    seq = result.scalar_one_or_none()
    if seq is None:
        seq = SequenceRecu(annee_scolaire_id=annee_id, dernier_numero=0)
        db.add(seq)
        await db.flush()
    seq.dernier_numero += 1
    annee = await db.get(AnneeScolaire, annee_id)
    year = annee.libelle[:4] if annee else "0000"
    return f"REC-{year}-{seq.dernier_numero:05d}"


def _paiement_to_response(
    p: Paiement,
    eleve: Eleve,
    type_libelle: str,
    tranche_libelle: str | None = None,
) -> PaiementResponse:
    return PaiementResponse(
        id=p.id,
        eleve_id=p.eleve_id,
        eleve_nom=eleve.nom,
        eleve_prenoms=eleve.prenoms,
        eleve_matricule=eleve.matricule,
        annee_scolaire_id=p.annee_scolaire_id,
        type_frais_id=p.type_frais_id,
        type_frais_libelle=type_libelle,
        tranche_id=p.tranche_id,
        tranche_libelle=tranche_libelle,
        montant=p.montant,
        remise_montant=p.remise_montant,
        mode_paiement=p.mode_paiement,
        reference_externe=p.reference_externe,
        date_paiement=p.date_paiement,
        numero_recu=p.numero_recu,
        statut=p.statut,
        libelle=p.libelle,
    )


async def list_tarifs(db: AsyncSession, annee_id: UUID) -> list[dict]:
    result = await db.execute(
        select(TarifNiveau, Niveau, TypeFrais)
        .join(Niveau, Niveau.id == TarifNiveau.niveau_id)
        .join(TypeFrais, TypeFrais.id == TarifNiveau.type_frais_id)
        .where(TarifNiveau.annee_scolaire_id == annee_id)
        .order_by(Niveau.ordre, TypeFrais.libelle)
    )
    return [
        {
            "id": t.id,
            "annee_scolaire_id": t.annee_scolaire_id,
            "niveau_id": t.niveau_id,
            "niveau_code": n.code,
            "niveau_libelle": n.libelle,
            "type_frais_id": t.type_frais_id,
            "type_frais_code": tf.code,
            "type_frais_libelle": tf.libelle,
            "montant": t.montant,
        }
        for t, n, tf in result.all()
    ]


async def create_tarif(db: AsyncSession, data: TarifNiveauCreate) -> TarifNiveau:
    existing = await db.execute(
        select(TarifNiveau).where(
            TarifNiveau.annee_scolaire_id == data.annee_scolaire_id,
            TarifNiveau.niveau_id == data.niveau_id,
            TarifNiveau.type_frais_id == data.type_frais_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tarif déjà défini pour ce niveau et type")
    tarif = TarifNiveau(**data.model_dump())
    db.add(tarif)
    await db.commit()
    await db.refresh(tarif)
    return tarif


async def list_tranches(db: AsyncSession, annee_id: UUID, type_frais_id: UUID | None = None) -> list[dict]:
    query = (
        select(TrancheFrais, TypeFrais)
        .join(TypeFrais, TypeFrais.id == TrancheFrais.type_frais_id)
        .where(TrancheFrais.annee_scolaire_id == annee_id)
        .order_by(TrancheFrais.type_frais_id, TrancheFrais.ordre)
    )
    if type_frais_id:
        query = query.where(TrancheFrais.type_frais_id == type_frais_id)
    result = await db.execute(query)
    return [
        {
            "id": tr.id,
            "annee_scolaire_id": tr.annee_scolaire_id,
            "type_frais_id": tr.type_frais_id,
            "type_frais_libelle": tf.libelle,
            "libelle": tr.libelle,
            "date_echeance": tr.date_echeance,
            "ordre": tr.ordre,
            "pourcentage": tr.pourcentage,
        }
        for tr, tf in result.all()
    ]


async def create_tranche(db: AsyncSession, data: TrancheFraisCreate) -> TrancheFrais:
    tranche = TrancheFrais(**data.model_dump())
    db.add(tranche)
    await db.commit()
    await db.refresh(tranche)
    return tranche


async def _calc_remise(
    db: AsyncSession,
    eleve_id: UUID,
    annee_id: UUID,
    type_frais_id: UUID,
    montant_base: Decimal,
) -> Decimal:
    result = await db.execute(
        select(RemiseEleve).where(
            RemiseEleve.eleve_id == eleve_id,
            RemiseEleve.annee_scolaire_id == annee_id,
            (RemiseEleve.type_frais_id == type_frais_id) | (RemiseEleve.type_frais_id.is_(None)),
        )
    )
    total_remise = Decimal("0")
    for remise in result.scalars().all():
        if remise.pourcentage:
            total_remise += montant_base * remise.pourcentage / Decimal("100")
        else:
            total_remise += remise.montant
    return total_remise


async def _montant_paye(
    db: AsyncSession,
    eleve_id: UUID,
    annee_id: UUID,
    type_frais_id: UUID | None = None,
    tranche_id: UUID | None = None,
) -> Decimal:
    query = select(func.coalesce(func.sum(Paiement.montant), 0)).where(
        Paiement.eleve_id == eleve_id,
        Paiement.annee_scolaire_id == annee_id,
        Paiement.statut == StatutPaiement.VALIDE.value,
    )
    if type_frais_id:
        query = query.where(Paiement.type_frais_id == type_frais_id)
    if tranche_id:
        query = query.where(Paiement.tranche_id == tranche_id)
    result = await db.execute(query)
    return Decimal(str(result.scalar_one()))


async def _log_paiement_historique(
    db: AsyncSession,
    paiement: Paiement,
    action: str,
    statut_avant: str | None,
    statut_apres: str,
    user_id: UUID | None,
    ip_address: str | None,
    details: str | None = None,
) -> None:
    from app.models.audit import HistoriquePaiement

    db.add(
        HistoriquePaiement(
            paiement_id=paiement.id,
            eleve_id=paiement.eleve_id,
            annee_scolaire_id=paiement.annee_scolaire_id,
            action=action,
            montant=paiement.montant,
            statut_avant=statut_avant,
            statut_apres=statut_apres,
            details=details,
            modifie_par_id=user_id,
            ip_address=ip_address,
        )
    )


async def create_paiement(
    db: AsyncSession,
    data: PaiementCreate,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_email: str | None = None,
) -> PaiementResponse:
    eleve = await db.get(Eleve, data.eleve_id)
    if eleve is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    annee = await parametrage_service.get_annee_active(db) if not data.annee_scolaire_id else await db.get(
        AnneeScolaire, data.annee_scolaire_id
    )
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")

    await parametrage_service.ensure_annee_modifiable(db, annee.id)

    type_frais = await db.get(TypeFrais, data.type_frais_id)
    if type_frais is None:
        raise HTTPException(status_code=404, detail="Type de frais introuvable")

    numero = await _next_numero_recu(db, annee.id)
    paiement = Paiement(
        eleve_id=data.eleve_id,
        annee_scolaire_id=annee.id,
        type_frais_id=data.type_frais_id,
        tranche_id=data.tranche_id,
        montant=data.montant,
        remise_montant=data.remise_montant,
        mode_paiement=data.mode_paiement,
        reference_externe=data.reference_externe,
        date_paiement=data.date_paiement or date.today(),
        numero_recu=numero,
        statut=StatutPaiement.VALIDE.value,
        encaisse_par_id=user_id,
        libelle=data.libelle,
    )
    db.add(paiement)
    await db.flush()
    await _log_paiement_historique(
        db, paiement, "create", None, paiement.statut, user_id, ip_address,
        details=f"Reçu {numero}",
    )
    from app.services import audit_service

    await audit_service.log_audit(
        db,
        action="create",
        resource_type="paiement",
        resource_id=str(paiement.id),
        details=f"Encaissement {numero} — {data.montant} GNF",
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
    )
    await db.commit()
    await db.refresh(paiement)

    tranche_lib = None
    if data.tranche_id:
        tr = await db.get(TrancheFrais, data.tranche_id)
        tranche_lib = tr.libelle if tr else None

    return _paiement_to_response(paiement, eleve, type_frais.libelle, tranche_lib)


async def get_paiement(db: AsyncSession, paiement_id: UUID) -> PaiementResponse:
    result = await db.execute(
        select(Paiement, Eleve, TypeFrais)
        .join(Eleve, Eleve.id == Paiement.eleve_id)
        .join(TypeFrais, TypeFrais.id == Paiement.type_frais_id)
        .where(Paiement.id == paiement_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    p, eleve, tf = row
    tranche_lib = None
    if p.tranche_id:
        tr = await db.get(TrancheFrais, p.tranche_id)
        tranche_lib = tr.libelle if tr else None
    return _paiement_to_response(p, eleve, tf.libelle, tranche_lib)


async def annuler_paiement(
    db: AsyncSession,
    paiement_id: UUID,
    data: PaiementAnnulation,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_email: str | None = None,
) -> PaiementResponse:
    p = await db.get(Paiement, paiement_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    if p.statut != StatutPaiement.VALIDE.value:
        raise HTTPException(status_code=422, detail="Seul un paiement valide peut être annulé")
    await parametrage_service.ensure_annee_modifiable(db, p.annee_scolaire_id)
    statut_avant = p.statut
    p.statut = StatutPaiement.ANNULE.value
    p.motif_annulation = data.motif
    await _log_paiement_historique(
        db, p, "annulation", statut_avant, p.statut, user_id, ip_address, details=data.motif,
    )
    from app.services import audit_service

    await audit_service.log_audit(
        db,
        action="annulation",
        resource_type="paiement",
        resource_id=str(p.id),
        details=data.motif,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
    )
    await db.commit()
    return await get_paiement(db, paiement_id)


async def rembourser_paiement(
    db: AsyncSession,
    paiement_id: UUID,
    data: PaiementRemboursement,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_email: str | None = None,
) -> PaiementResponse:
    origine = await db.get(Paiement, paiement_id)
    if origine is None:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    if origine.statut != StatutPaiement.VALIDE.value:
        raise HTTPException(status_code=422, detail="Seul un paiement valide peut être remboursé")

    await parametrage_service.ensure_annee_modifiable(db, origine.annee_scolaire_id)
    statut_avant = origine.statut
    origine.statut = StatutPaiement.REMBOURSE.value
    origine.motif_annulation = data.motif

    numero = await _next_numero_recu(db, origine.annee_scolaire_id)
    remboursement = Paiement(
        eleve_id=origine.eleve_id,
        annee_scolaire_id=origine.annee_scolaire_id,
        type_frais_id=origine.type_frais_id,
        tranche_id=origine.tranche_id,
        montant=-origine.montant,
        remise_montant=Decimal("0"),
        mode_paiement=data.mode_paiement,
        date_paiement=date.today(),
        numero_recu=numero,
        statut=StatutPaiement.VALIDE.value,
        encaisse_par_id=user_id,
        paiement_origine_id=origine.id,
        libelle=f"Remboursement — {data.motif}",
    )
    db.add(remboursement)
    await db.flush()
    await _log_paiement_historique(
        db, origine, "remboursement", statut_avant, origine.statut, user_id, ip_address, details=data.motif,
    )
    from app.services import audit_service

    await audit_service.log_audit(
        db,
        action="update",
        resource_type="paiement",
        resource_id=str(origine.id),
        details=f"Remboursement — {data.motif}",
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
    )
    await db.commit()
    return await get_paiement(db, remboursement.id)


async def get_situation_eleve(
    db: AsyncSession,
    eleve_id: UUID,
    annee_id: UUID | None = None,
) -> SituationEleveResponse:
    eleve = await db.get(Eleve, eleve_id)
    if eleve is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    annee = await parametrage_service.get_annee_active(db) if not annee_id else await db.get(
        AnneeScolaire, annee_id
    )
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")

    niveau_id = await _get_eleve_niveau(db, eleve_id, annee.id)

    tarifs_result = await db.execute(
        select(TarifNiveau, TypeFrais)
        .join(TypeFrais, TypeFrais.id == TarifNiveau.type_frais_id)
        .where(
            TarifNiveau.annee_scolaire_id == annee.id,
            TarifNiveau.niveau_id == niveau_id,
            TypeFrais.actif.is_(True),
        )
    )

    lignes: list[LigneSituation] = []
    tranches_sit: list[TrancheSituation] = []
    total_du = Decimal("0")
    total_paye = Decimal("0")

    for tarif, tf in tarifs_result.all():
        remise = await _calc_remise(db, eleve_id, annee.id, tf.id, tarif.montant)
        montant_du = max(tarif.montant - remise, Decimal("0"))
        paye = await _montant_paye(db, eleve_id, annee.id, tf.id)
        restant = max(montant_du - paye, Decimal("0"))
        total_du += montant_du
        total_paye += paye
        lignes.append(
            LigneSituation(
                type_frais_id=tf.id,
                type_frais_code=tf.code,
                type_frais_libelle=tf.libelle,
                montant_du=montant_du,
                montant_paye=paye,
                montant_restant=restant,
                remise=remise,
            )
        )

    tranches_result = await db.execute(
        select(TrancheFrais, TypeFrais)
        .join(TypeFrais, TypeFrais.id == TrancheFrais.type_frais_id)
        .where(TrancheFrais.annee_scolaire_id == annee.id)
        .order_by(TrancheFrais.ordre)
    )
    today = date.today()
    for tranche, tf in tranches_result.all():
        tarif_row = await db.execute(
            select(TarifNiveau).where(
                TarifNiveau.annee_scolaire_id == annee.id,
                TarifNiveau.niveau_id == niveau_id,
                TarifNiveau.type_frais_id == tranche.type_frais_id,
            )
        )
        tarif = tarif_row.scalar_one_or_none()
        if tarif is None:
            continue
        remise = await _calc_remise(db, eleve_id, annee.id, tf.id, tarif.montant)
        base = max(tarif.montant - remise, Decimal("0"))
        montant_tranche = (base * tranche.pourcentage / Decimal("100")).quantize(Decimal("0.01"))
        paye_tr = await _montant_paye(db, eleve_id, annee.id, tf.id, tranche.id)
        tranches_sit.append(
            TrancheSituation(
                tranche_id=tranche.id,
                libelle=f"{tf.libelle} — {tranche.libelle}",
                date_echeance=tranche.date_echeance,
                montant_du=montant_tranche,
                montant_paye=paye_tr,
                en_retard=tranche.date_echeance < today and paye_tr < montant_tranche,
            )
        )

    return SituationEleveResponse(
        eleve_id=eleve.id,
        matricule=eleve.matricule,
        nom=eleve.nom,
        prenoms=eleve.prenoms,
        annee_scolaire_id=annee.id,
        annee_libelle=annee.libelle,
        total_du=total_du,
        total_paye=total_paye,
        total_restant=max(total_du - total_paye, Decimal("0")),
        lignes=lignes,
        tranches=tranches_sit,
    )


async def list_impayes(
    db: AsyncSession,
    annee_id: UUID | None = None,
    classe_id: UUID | None = None,
) -> list[ImpayeItem]:
    annee = await parametrage_service.get_annee_active(db) if not annee_id else await db.get(
        AnneeScolaire, annee_id
    )
    if annee is None:
        return []

    query = (
        select(Eleve)
        .join(Inscription, Inscription.eleve_id == Eleve.id)
        .where(
            Inscription.annee_scolaire_id == annee.id,
            Inscription.statut == StatutEleve.ACTIF.value,
            Eleve.statut == StatutEleve.ACTIF.value,
        )
    )
    if classe_id:
        query = query.where(Inscription.classe_id == classe_id)

    eleves = list((await db.execute(query)).scalars().all())
    items: list[ImpayeItem] = []

    for eleve in eleves:
        sit = await get_situation_eleve(db, eleve.id, annee.id)
        if sit.total_restant <= 0:
            continue

        classe_nom = None
        if classe_id:
            cl = await db.get(Classe, classe_id)
            classe_nom = cl.nom if cl else None
        else:
            ins = await db.execute(
                select(Inscription, Classe)
                .outerjoin(Classe, Classe.id == Inscription.classe_id)
                .where(
                    Inscription.eleve_id == eleve.id,
                    Inscription.annee_scolaire_id == annee.id,
                )
            )
            row = ins.first()
            if row and row[1]:
                classe_nom = row[1].nom

        tranches_retard = sum(1 for t in sit.tranches if t.en_retard)

        rel_result = await db.execute(
            select(RelanceImpaye.date_relance)
            .where(RelanceImpaye.eleve_id == eleve.id, RelanceImpaye.annee_scolaire_id == annee.id)
            .order_by(RelanceImpaye.date_relance.desc())
            .limit(1)
        )
        derniere = rel_result.scalar_one_or_none()

        items.append(
            ImpayeItem(
                eleve_id=eleve.id,
                matricule=eleve.matricule,
                nom=eleve.nom,
                prenoms=eleve.prenoms,
                classe_nom=classe_nom,
                montant_du=sit.total_du,
                montant_paye=sit.total_paye,
                montant_restant=sit.total_restant,
                tranches_en_retard=tranches_retard,
                derniere_relance=derniere,
            )
        )

    items.sort(key=lambda x: x.montant_restant, reverse=True)
    return items


async def create_relance(db: AsyncSession, data: RelanceCreate) -> RelanceImpaye:
    annee = await parametrage_service.get_annee_active(db) if not data.annee_scolaire_id else await db.get(
        AnneeScolaire, data.annee_scolaire_id
    )
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")

    relance = RelanceImpaye(
        eleve_id=data.eleve_id,
        annee_scolaire_id=annee.id,
        tranche_id=data.tranche_id,
        date_relance=date.today(),
        canal=data.canal,
        message=data.message,
    )
    db.add(relance)
    await db.commit()
    await db.refresh(relance)
    return relance


async def create_remise(db: AsyncSession, data: RemiseEleveCreate) -> RemiseEleve:
    remise = RemiseEleve(**data.model_dump())
    db.add(remise)
    await db.commit()
    await db.refresh(remise)
    return remise


async def get_caisse_journaliere(
    db: AsyncSession,
    target_date: date,
) -> CaisseJournaliereResponse:
    result = await db.execute(
        select(Paiement, Eleve, TypeFrais)
        .join(Eleve, Eleve.id == Paiement.eleve_id)
        .join(TypeFrais, TypeFrais.id == Paiement.type_frais_id)
        .where(
            Paiement.date_paiement == target_date,
            Paiement.statut == StatutPaiement.VALIDE.value,
        )
        .order_by(Paiement.created_at.desc())
    )
    rows = result.all()
    par_mode: dict[str, Decimal] = {}
    paiements: list[PaiementResponse] = []
    total = Decimal("0")

    for p, eleve, tf in rows:
        par_mode[p.mode_paiement] = par_mode.get(p.mode_paiement, Decimal("0")) + p.montant
        total += p.montant
        tranche_lib = None
        if p.tranche_id:
            tr = await db.get(TrancheFrais, p.tranche_id)
            tranche_lib = tr.libelle if tr else None
        paiements.append(_paiement_to_response(p, eleve, tf.libelle, tranche_lib))

    return CaisseJournaliereResponse(
        date=target_date,
        total_encaisse=total,
        nombre_paiements=len(paiements),
        par_mode=par_mode,
        paiements=paiements,
    )


async def generate_recu_pdf(db: AsyncSession, paiement_id: UUID) -> bytes:
    paiement_resp = await get_paiement(db, paiement_id)
    etab = await parametrage_service.get_etablissement(db)
    return pdf_service.generate_recu_paiement(paiement_resp, etab)
