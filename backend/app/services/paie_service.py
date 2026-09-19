import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paie import (
    AvanceSalaire,
    BulletinPaie,
    PeriodePaie,
    StatutAvance,
    StatutBulletinPaie,
    StatutPeriodePaie,
)
from app.models.personnel import (
    CongeAbsence,
    Contrat,
    Personnel,
    StatutConge,
    StatutContrat,
    StatutPersonnel,
)
from app.models.user import User
from app.schemas.paie import (
    AvanceSalaireCreate,
    BulletinPaieResponse,
    BulletinPaieUpdate,
    MasseSalarialeResponse,
    PeriodePaieCreate,
)
from app.services import parametrage_service, pdf_service

TAUX_CNSS = Decimal("0.05")
TAUX_ITS = Decimal("0.15")
INDEMNITE_TRANSPORT = Decimal("200000")


def _q(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _periode_libelle(annee: int, mois: int) -> str:
    mois_noms = [
        "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
    ]
    return f"{mois_noms[mois]} {annee}"


def _mois_bounds(annee: int, mois: int) -> tuple[date, date]:
    last = calendar.monthrange(annee, mois)[1]
    return date(annee, mois, 1), date(annee, mois, last)


async def _get_contrat_actif(db: AsyncSession, personnel_id: UUID) -> Contrat | None:
    result = await db.execute(
        select(Contrat).where(
            Contrat.personnel_id == personnel_id,
            Contrat.statut == StatutContrat.ACTIF.value,
        ).order_by(Contrat.date_debut.desc())
    )
    return result.scalars().first()


async def _jours_absence_mois(db: AsyncSession, personnel_id: UUID, annee: int, mois: int) -> int:
    debut, fin = _mois_bounds(annee, mois)
    result = await db.execute(
        select(CongeAbsence).where(
            CongeAbsence.personnel_id == personnel_id,
            CongeAbsence.statut == StatutConge.APPROUVE.value,
            CongeAbsence.type.in_(["absence", "maladie"]),
            CongeAbsence.date_debut <= fin,
            CongeAbsence.date_fin >= debut,
        )
    )
    total = 0
    for conge in result.scalars().all():
        start = max(conge.date_debut, debut)
        end = min(conge.date_fin, fin)
        total += (end - start).days + 1
    return total


async def _total_avances_actives(db: AsyncSession, personnel_id: UUID) -> Decimal:
    result = await db.execute(
        select(func.coalesce(func.sum(AvanceSalaire.montant), 0)).where(
            AvanceSalaire.personnel_id == personnel_id,
            AvanceSalaire.statut == StatutAvance.ACTIVE.value,
        )
    )
    return Decimal(str(result.scalar_one()))


def _calculer_montants(
    salaire_base: Decimal,
    jours_absence: int,
    retenue_avances: Decimal,
    prime_autre: Decimal = Decimal("0"),
    indemnite_logement: Decimal = Decimal("0"),
    autres_retenues: Decimal = Decimal("0"),
) -> dict[str, Decimal | int]:
    prime_anciennete = Decimal("0")
    indemnite_transport = INDEMNITE_TRANSPORT
    retenue_absences = _q((salaire_base / Decimal("30")) * Decimal(jours_absence))
    brut = _q(salaire_base + prime_anciennete + prime_autre + indemnite_transport + indemnite_logement)
    retenue_cnss = _q(brut * TAUX_CNSS)
    base_its = max(brut - retenue_cnss, Decimal("0"))
    retenue_its = _q(base_its * TAUX_ITS)
    net = _q(
        brut - retenue_cnss - retenue_its - retenue_absences - retenue_avances - autres_retenues
    )
    return {
        "prime_anciennete": prime_anciennete,
        "indemnite_transport": indemnite_transport,
        "retenue_absences": retenue_absences,
        "retenue_cnss": retenue_cnss,
        "retenue_its": retenue_its,
        "brut": brut,
        "net_a_payer": max(net, Decimal("0")),
        "jours_absence": jours_absence,
    }


async def _bulletin_to_response(
    db: AsyncSession,
    bulletin: BulletinPaie,
    personnel: Personnel,
    periode: PeriodePaie,
) -> BulletinPaieResponse:
    return BulletinPaieResponse(
        id=bulletin.id,
        personnel_id=personnel.id,
        personnel_matricule=personnel.matricule,
        personnel_nom=personnel.nom,
        personnel_prenoms=personnel.prenoms,
        periode_paie_id=periode.id,
        periode_libelle=periode.libelle,
        salaire_base=bulletin.salaire_base,
        prime_anciennete=bulletin.prime_anciennete,
        prime_autre=bulletin.prime_autre,
        indemnite_transport=bulletin.indemnite_transport,
        indemnite_logement=bulletin.indemnite_logement,
        retenue_cnss=bulletin.retenue_cnss,
        retenue_its=bulletin.retenue_its,
        retenue_absences=bulletin.retenue_absences,
        retenue_avances=bulletin.retenue_avances,
        autres_retenues=bulletin.autres_retenues,
        brut=bulletin.brut,
        net_a_payer=bulletin.net_a_payer,
        jours_absence=bulletin.jours_absence,
        statut=bulletin.statut,
    )


async def list_periodes(db: AsyncSession) -> list[PeriodePaie]:
    result = await db.execute(select(PeriodePaie).order_by(PeriodePaie.annee.desc(), PeriodePaie.mois.desc()))
    return list(result.scalars().all())


async def create_periode(db: AsyncSession, data: PeriodePaieCreate) -> PeriodePaie:
    existing = await db.execute(
        select(PeriodePaie).where(PeriodePaie.annee == data.annee, PeriodePaie.mois == data.mois)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Période de paie déjà existante")

    periode = PeriodePaie(
        annee=data.annee,
        mois=data.mois,
        libelle=_periode_libelle(data.annee, data.mois),
    )
    db.add(periode)
    await db.commit()
    await db.refresh(periode)
    return periode


async def _build_bulletin(
    db: AsyncSession,
    personnel: Personnel,
    periode: PeriodePaie,
    existing: BulletinPaie | None = None,
) -> BulletinPaie:
    contrat = await _get_contrat_actif(db, personnel.id)
    if contrat is None or contrat.salaire_mensuel is None:
        raise HTTPException(
            status_code=422,
            detail=f"Aucun contrat actif avec salaire pour {personnel.matricule}",
        )

    jours = await _jours_absence_mois(db, personnel.id, periode.annee, periode.mois)
    avances = await _total_avances_actives(db, personnel.id)

    prime_autre = existing.prime_autre if existing else Decimal("0")
    indemnite_logement = existing.indemnite_logement if existing else Decimal("0")
    autres_retenues = existing.autres_retenues if existing else Decimal("0")

    calc = _calculer_montants(
        Decimal(str(contrat.salaire_mensuel)),
        jours,
        avances,
        prime_autre,
        indemnite_logement,
        autres_retenues,
    )

    if existing:
        bulletin = existing
    else:
        bulletin = BulletinPaie(personnel_id=personnel.id, periode_paie_id=periode.id)
        db.add(bulletin)

    bulletin.salaire_base = Decimal(str(contrat.salaire_mensuel))
    bulletin.prime_anciennete = calc["prime_anciennete"]  # type: ignore[assignment]
    bulletin.prime_autre = prime_autre
    bulletin.indemnite_transport = calc["indemnite_transport"]  # type: ignore[assignment]
    bulletin.indemnite_logement = indemnite_logement
    bulletin.retenue_cnss = calc["retenue_cnss"]  # type: ignore[assignment]
    bulletin.retenue_its = calc["retenue_its"]  # type: ignore[assignment]
    bulletin.retenue_absences = calc["retenue_absences"]  # type: ignore[assignment]
    bulletin.retenue_avances = avances
    bulletin.autres_retenues = autres_retenues
    bulletin.brut = calc["brut"]  # type: ignore[assignment]
    bulletin.net_a_payer = calc["net_a_payer"]  # type: ignore[assignment]
    bulletin.jours_absence = calc["jours_absence"]  # type: ignore[assignment]
    if not existing:
        bulletin.statut = StatutBulletinPaie.BROUILLON.value

    await db.flush()
    return bulletin


async def generer_paie_mensuelle(db: AsyncSession, periode_id: UUID) -> list[BulletinPaieResponse]:
    periode = await db.get(PeriodePaie, periode_id)
    if periode is None:
        raise HTTPException(status_code=404, detail="Période introuvable")
    if periode.statut == StatutPeriodePaie.CLOTUREE.value:
        raise HTTPException(status_code=422, detail="Période clôturée")

    result = await db.execute(
        select(Personnel).where(Personnel.statut == StatutPersonnel.ACTIF.value)
    )
    personnel_list = list(result.scalars().all())
    responses: list[BulletinPaieResponse] = []

    for pers in personnel_list:
        existing_result = await db.execute(
            select(BulletinPaie).where(
                BulletinPaie.personnel_id == pers.id,
                BulletinPaie.periode_paie_id == periode_id,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing and existing.statut == StatutBulletinPaie.PAYE.value:
            continue
        try:
            bulletin = await _build_bulletin(db, pers, periode, existing)
            responses.append(await _bulletin_to_response(db, bulletin, pers, periode))
        except HTTPException:
            continue

    await db.commit()
    return responses


async def list_bulletins(
    db: AsyncSession,
    periode_id: UUID | None = None,
    personnel_id: UUID | None = None,
) -> list[BulletinPaieResponse]:
    query = (
        select(BulletinPaie, Personnel, PeriodePaie)
        .join(Personnel, Personnel.id == BulletinPaie.personnel_id)
        .join(PeriodePaie, PeriodePaie.id == BulletinPaie.periode_paie_id)
        .order_by(Personnel.nom)
    )
    if periode_id:
        query = query.where(BulletinPaie.periode_paie_id == periode_id)
    if personnel_id:
        query = query.where(BulletinPaie.personnel_id == personnel_id)

    result = await db.execute(query)
    return [
        await _bulletin_to_response(db, b, p, per)
        for b, p, per in result.all()
    ]


async def get_bulletin(db: AsyncSession, bulletin_id: UUID) -> BulletinPaieResponse:
    result = await db.execute(
        select(BulletinPaie, Personnel, PeriodePaie)
        .join(Personnel, Personnel.id == BulletinPaie.personnel_id)
        .join(PeriodePaie, PeriodePaie.id == BulletinPaie.periode_paie_id)
        .where(BulletinPaie.id == bulletin_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Bulletin introuvable")
    return await _bulletin_to_response(db, row[0], row[1], row[2])


async def update_bulletin(
    db: AsyncSession,
    bulletin_id: UUID,
    data: BulletinPaieUpdate,
) -> BulletinPaieResponse:
    result = await db.execute(
        select(BulletinPaie, Personnel, PeriodePaie)
        .join(Personnel, Personnel.id == BulletinPaie.personnel_id)
        .join(PeriodePaie, PeriodePaie.id == BulletinPaie.periode_paie_id)
        .where(BulletinPaie.id == bulletin_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Bulletin introuvable")
    bulletin, pers, periode = row
    if bulletin.statut == StatutBulletinPaie.PAYE.value:
        raise HTTPException(status_code=422, detail="Bulletin déjà payé")

    if data.prime_autre is not None:
        bulletin.prime_autre = data.prime_autre
    if data.indemnite_logement is not None:
        bulletin.indemnite_logement = data.indemnite_logement
    if data.autres_retenues is not None:
        bulletin.autres_retenues = data.autres_retenues

    await _build_bulletin(db, pers, periode, bulletin)
    await db.commit()
    return await get_bulletin(db, bulletin_id)


async def valider_bulletin(db: AsyncSession, bulletin_id: UUID) -> BulletinPaieResponse:
    bulletin = await db.get(BulletinPaie, bulletin_id)
    if bulletin is None:
        raise HTTPException(status_code=404, detail="Bulletin introuvable")
    bulletin.statut = StatutBulletinPaie.VALIDE.value
    await db.commit()
    return await get_bulletin(db, bulletin_id)


async def payer_bulletin(
    db: AsyncSession,
    bulletin_id: UUID,
    user_id: UUID | None = None,
) -> BulletinPaieResponse:
    bulletin = await db.get(BulletinPaie, bulletin_id)
    if bulletin is None:
        raise HTTPException(status_code=404, detail="Bulletin introuvable")
    if bulletin.statut not in (StatutBulletinPaie.VALIDE.value, StatutBulletinPaie.BROUILLON.value):
        raise HTTPException(status_code=422, detail="Bulletin non payable")

    bulletin.statut = StatutBulletinPaie.PAYE.value
    bulletin.paye_par_id = user_id

    avances = await db.execute(
        select(AvanceSalaire).where(
            AvanceSalaire.personnel_id == bulletin.personnel_id,
            AvanceSalaire.statut == StatutAvance.ACTIVE.value,
        )
    )
    for av in avances.scalars().all():
        av.statut = StatutAvance.REMBOURSEE.value
        av.bulletin_paie_id = bulletin.id

    await db.commit()
    return await get_bulletin(db, bulletin_id)


async def create_avance(db: AsyncSession, data: AvanceSalaireCreate) -> AvanceSalaire:
    pers = await db.get(Personnel, data.personnel_id)
    if pers is None:
        raise HTTPException(status_code=404, detail="Personnel introuvable")

    avance = AvanceSalaire(
        personnel_id=data.personnel_id,
        montant=data.montant,
        date_avance=date.fromisoformat(data.date_avance),
        motif=data.motif,
    )
    db.add(avance)
    await db.commit()
    await db.refresh(avance)
    return avance


async def list_avances(db: AsyncSession, personnel_id: UUID | None = None) -> list[dict]:
    query = (
        select(AvanceSalaire, Personnel)
        .join(Personnel, Personnel.id == AvanceSalaire.personnel_id)
        .order_by(AvanceSalaire.date_avance.desc())
    )
    if personnel_id:
        query = query.where(AvanceSalaire.personnel_id == personnel_id)

    result = await db.execute(query)
    return [
        {
            "id": a.id,
            "personnel_id": a.personnel_id,
            "personnel_nom": p.nom,
            "personnel_prenoms": p.prenoms,
            "montant": a.montant,
            "date_avance": a.date_avance,
            "motif": a.motif,
            "statut": a.statut,
        }
        for a, p in result.all()
    ]


async def get_masse_salariale(db: AsyncSession, periode_id: UUID) -> MasseSalarialeResponse:
    periode = await db.get(PeriodePaie, periode_id)
    if periode is None:
        raise HTTPException(status_code=404, detail="Période introuvable")

    bulletins = await list_bulletins(db, periode_id=periode_id)
    total_brut = sum(b.brut for b in bulletins)
    total_net = sum(b.net_a_payer for b in bulletins)
    total_cnss = sum(b.retenue_cnss for b in bulletins)
    total_its = sum(b.retenue_its for b in bulletins)
    total_paye = sum(b.net_a_payer for b in bulletins if b.statut == StatutBulletinPaie.PAYE.value)
    total_a_payer = total_net - total_paye

    return MasseSalarialeResponse(
        periode_paie_id=periode.id,
        periode_libelle=periode.libelle,
        nombre_bulletins=len(bulletins),
        total_brut=total_brut,
        total_net=total_net,
        total_cnss=total_cnss,
        total_its=total_its,
        total_paye=total_paye,
        total_a_payer=total_a_payer,
        bulletins=bulletins,
    )


async def get_mes_bulletins(db: AsyncSession, user_id: UUID) -> list[BulletinPaieResponse]:
    result = await db.execute(select(Personnel).where(Personnel.user_id == user_id))
    pers = result.scalar_one_or_none()
    if pers is None:
        return []
    return await list_bulletins(db, personnel_id=pers.id)


async def generate_bulletin_pdf(db: AsyncSession, bulletin_id: UUID) -> bytes:
    bulletin = await get_bulletin(db, bulletin_id)
    etab = await parametrage_service.get_etablissement(db)
    return pdf_service.generate_bulletin_paie(bulletin, etab)
