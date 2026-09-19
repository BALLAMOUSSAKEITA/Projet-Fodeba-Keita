import csv
import io
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comptabilite import (
    BudgetLigne,
    CategorieDepense,
    CompteTresorerie,
    Depense,
    EcritureComptable,
    StatutDepense,
    TypeEcriture,
)
from app.models.paiements import Paiement, StatutPaiement
from app.models.parametrage import AnneeScolaire
from app.schemas.comptabilite import (
    BudgetLigneCreate,
    BudgetSuiviItem,
    BudgetSuiviResponse,
    DepenseCreate,
    DepenseRefus,
    DepenseResponse,
    EcritureResponse,
    RapportFinancierResponse,
    TresorerieResponse,
)
from app.services import parametrage_service


async def list_categories(db: AsyncSession) -> list[CategorieDepense]:
    result = await db.execute(
        select(CategorieDepense).where(CategorieDepense.actif.is_(True)).order_by(CategorieDepense.libelle)
    )
    return list(result.scalars().all())


async def list_comptes(db: AsyncSession) -> list[CompteTresorerie]:
    result = await db.execute(
        select(CompteTresorerie).where(CompteTresorerie.actif.is_(True)).order_by(CompteTresorerie.code)
    )
    return list(result.scalars().all())


async def list_comptes_avec_solde(db: AsyncSession) -> list[dict]:
    from app.schemas.comptabilite import CompteTresorerieResponse

    comptes = await list_comptes(db)
    return [
        CompteTresorerieResponse(
            id=c.id,
            code=c.code,
            libelle=c.libelle,
            type=c.type,
            solde_initial=c.solde_initial,
            solde_actuel=await _solde_compte(db, c.id),
            actif=c.actif,
        )
        for c in comptes
    ]


async def _solde_compte(db: AsyncSession, compte_id: UUID) -> Decimal:
    compte = await db.get(CompteTresorerie, compte_id)
    if compte is None:
        return Decimal("0")
    recettes = await db.execute(
        select(func.coalesce(func.sum(EcritureComptable.montant), 0)).where(
            EcritureComptable.compte_tresorerie_id == compte_id,
            EcritureComptable.type == TypeEcriture.RECETTE.value,
        )
    )
    depenses = await db.execute(
        select(func.coalesce(func.sum(EcritureComptable.montant), 0)).where(
            EcritureComptable.compte_tresorerie_id == compte_id,
            EcritureComptable.type == TypeEcriture.DEPENSE.value,
        )
    )
    return compte.solde_initial + Decimal(str(recettes.scalar_one())) - Decimal(str(depenses.scalar_one()))


async def get_tresorerie(db: AsyncSession) -> TresorerieResponse:
    comptes = await list_comptes(db)
    items = []
    total_caisse = Decimal("0")
    total_banque = Decimal("0")
    for c in comptes:
        solde = await _solde_compte(db, c.id)
        items.append({
            "id": c.id,
            "code": c.code,
            "libelle": c.libelle,
            "type": c.type,
            "solde_initial": c.solde_initial,
            "solde_actuel": solde,
            "actif": c.actif,
        })
        if c.type == "caisse":
            total_caisse += solde
        else:
            total_banque += solde

    from app.schemas.comptabilite import CompteTresorerieResponse

    return TresorerieResponse(
        comptes=[CompteTresorerieResponse(**i) for i in items],
        total_caisse=total_caisse,
        total_banque=total_banque,
        total_general=total_caisse + total_banque,
    )


async def _depense_to_response(db: AsyncSession, d: Depense) -> DepenseResponse:
    cat = await db.get(CategorieDepense, d.categorie_id)
    compte = await db.get(CompteTresorerie, d.compte_tresorerie_id)
    return DepenseResponse(
        id=d.id,
        categorie_id=d.categorie_id,
        categorie_libelle=cat.libelle if cat else "—",
        annee_scolaire_id=d.annee_scolaire_id,
        libelle=d.libelle,
        montant=d.montant,
        date_depense=d.date_depense,
        compte_tresorerie_id=d.compte_tresorerie_id,
        compte_libelle=compte.libelle if compte else "—",
        statut=d.statut,
        reference_piece=d.reference_piece,
        motif_refus=d.motif_refus,
    )


async def create_depense(
    db: AsyncSession,
    data: DepenseCreate,
    user_id: UUID | None = None,
) -> DepenseResponse:
    annee = await parametrage_service.get_annee_active(db) if not data.annee_scolaire_id else await db.get(
        AnneeScolaire, data.annee_scolaire_id
    )
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")

    depense = Depense(
        categorie_id=data.categorie_id,
        annee_scolaire_id=annee.id,
        libelle=data.libelle,
        montant=data.montant,
        date_depense=data.date_depense,
        compte_tresorerie_id=data.compte_tresorerie_id,
        reference_piece=data.reference_piece,
        statut=StatutDepense.BROUILLON.value,
        saisi_par_id=user_id,
    )
    db.add(depense)
    await db.commit()
    await db.refresh(depense)
    return await _depense_to_response(db, depense)


async def list_depenses(
    db: AsyncSession,
    statut: str | None = None,
    annee_id: UUID | None = None,
) -> list[DepenseResponse]:
    query = select(Depense).order_by(Depense.date_depense.desc())
    if statut:
        query = query.where(Depense.statut == statut)
    if annee_id:
        query = query.where(Depense.annee_scolaire_id == annee_id)
    result = await db.execute(query)
    depenses = list(result.scalars().all())
    return [await _depense_to_response(db, d) for d in depenses]


async def soumettre_depense(db: AsyncSession, depense_id: UUID) -> DepenseResponse:
    depense = await db.get(Depense, depense_id)
    if depense is None:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    if depense.statut != StatutDepense.BROUILLON.value:
        raise HTTPException(status_code=422, detail="Dépense déjà soumise")
    depense.statut = StatutDepense.SOUMISE.value
    await db.commit()
    return await _depense_to_response(db, depense)


async def _creer_ecriture_depense(db: AsyncSession, depense: Depense) -> None:
    existing = await db.execute(
        select(EcritureComptable).where(
            EcritureComptable.source_type == "depense",
            EcritureComptable.source_id == depense.id,
        )
    )
    if existing.scalar_one_or_none():
        return
    db.add(
        EcritureComptable(
            date_ecriture=depense.date_depense,
            type=TypeEcriture.DEPENSE.value,
            libelle=depense.libelle,
            montant=depense.montant,
            compte_tresorerie_id=depense.compte_tresorerie_id,
            source_type="depense",
            source_id=depense.id,
            annee_scolaire_id=depense.annee_scolaire_id,
        )
    )


async def valider_depense(
    db: AsyncSession,
    depense_id: UUID,
    user_id: UUID | None = None,
) -> DepenseResponse:
    depense = await db.get(Depense, depense_id)
    if depense is None:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    if depense.statut != StatutDepense.SOUMISE.value:
        raise HTTPException(status_code=422, detail="Dépense non soumise")
    depense.statut = StatutDepense.VALIDEE.value
    depense.valide_par_id = user_id
    await _creer_ecriture_depense(db, depense)
    await db.commit()
    return await _depense_to_response(db, depense)


async def refuser_depense(
    db: AsyncSession,
    depense_id: UUID,
    data: DepenseRefus,
    user_id: UUID | None = None,
) -> DepenseResponse:
    depense = await db.get(Depense, depense_id)
    if depense is None:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    if depense.statut != StatutDepense.SOUMISE.value:
        raise HTTPException(status_code=422, detail="Dépense non soumise")
    depense.statut = StatutDepense.REFUSEE.value
    depense.motif_refus = data.motif
    depense.valide_par_id = user_id
    await db.commit()
    return await _depense_to_response(db, depense)


async def upsert_budget_ligne(db: AsyncSession, data: BudgetLigneCreate) -> BudgetLigne:
    result = await db.execute(
        select(BudgetLigne).where(
            BudgetLigne.annee_scolaire_id == data.annee_scolaire_id,
            BudgetLigne.categorie_id == data.categorie_id,
        )
    )
    ligne = result.scalar_one_or_none()
    if ligne:
        ligne.montant_prevu = data.montant_prevu
    else:
        ligne = BudgetLigne(**data.model_dump())
        db.add(ligne)
    await db.commit()
    await db.refresh(ligne)
    return ligne


async def get_budget_suivi(db: AsyncSession, annee_id: UUID) -> BudgetSuiviResponse:
    annee = await db.get(AnneeScolaire, annee_id)
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")

    budget_result = await db.execute(
        select(BudgetLigne, CategorieDepense)
        .join(CategorieDepense, CategorieDepense.id == BudgetLigne.categorie_id)
        .where(BudgetLigne.annee_scolaire_id == annee_id)
    )
    lignes: list[BudgetSuiviItem] = []
    total_prevu = Decimal("0")
    total_realise = Decimal("0")

    for budget, cat in budget_result.all():
        dep_result = await db.execute(
            select(func.coalesce(func.sum(Depense.montant), 0)).where(
                Depense.categorie_id == cat.id,
                Depense.annee_scolaire_id == annee_id,
                Depense.statut == StatutDepense.VALIDEE.value,
            )
        )
        realise = Decimal(str(dep_result.scalar_one()))
        prevu = budget.montant_prevu
        ecart = prevu - realise
        taux = (realise / prevu * Decimal("100")).quantize(Decimal("0.01")) if prevu > 0 else None
        lignes.append(
            BudgetSuiviItem(
                categorie_id=cat.id,
                categorie_code=cat.code,
                categorie_libelle=cat.libelle,
                montant_prevu=prevu,
                montant_realise=realise,
                ecart=ecart,
                taux_realisation=taux,
            )
        )
        total_prevu += prevu
        total_realise += realise

    return BudgetSuiviResponse(
        annee_scolaire_id=annee_id,
        annee_libelle=annee.libelle,
        total_prevu=total_prevu,
        total_realise=total_realise,
        lignes=lignes,
    )


async def sync_recettes_paiements(db: AsyncSession, annee_id: UUID) -> int:
    """Synchronise les paiements validés vers le journal comptable."""
    caisse_result = await db.execute(
        select(CompteTresorerie).where(CompteTresorerie.code == "CAISSE").limit(1)
    )
    caisse = caisse_result.scalar_one_or_none()
    if caisse is None:
        return 0

    paiements = await db.execute(
        select(Paiement).where(
            Paiement.annee_scolaire_id == annee_id,
            Paiement.statut == StatutPaiement.VALIDE.value,
            Paiement.montant > 0,
        )
    )
    count = 0
    for p in paiements.scalars().all():
        existing = await db.execute(
            select(EcritureComptable.id).where(
                EcritureComptable.source_type == "paiement",
                EcritureComptable.source_id == p.id,
            )
        )
        if existing.scalar_one_or_none():
            continue
        db.add(
            EcritureComptable(
                date_ecriture=p.date_paiement,
                type=TypeEcriture.RECETTE.value,
                libelle=f"Paiement {p.numero_recu}",
                montant=p.montant,
                compte_tresorerie_id=caisse.id,
                source_type="paiement",
                source_id=p.id,
                annee_scolaire_id=annee_id,
            )
        )
        count += 1
    if count:
        await db.commit()
    return count


async def list_journal(
    db: AsyncSession,
    date_debut: date | None = None,
    date_fin: date | None = None,
) -> list[EcritureResponse]:
    query = (
        select(EcritureComptable, CompteTresorerie)
        .join(CompteTresorerie, CompteTresorerie.id == EcritureComptable.compte_tresorerie_id)
        .order_by(EcritureComptable.date_ecriture.desc())
    )
    if date_debut:
        query = query.where(EcritureComptable.date_ecriture >= date_debut)
    if date_fin:
        query = query.where(EcritureComptable.date_ecriture <= date_fin)

    result = await db.execute(query)
    return [
        EcritureResponse(
            id=e.id,
            date_ecriture=e.date_ecriture,
            type=e.type,
            libelle=e.libelle,
            montant=e.montant,
            compte_libelle=c.libelle,
            source_type=e.source_type,
        )
        for e, c in result.all()
    ]


async def get_rapport_financier(
    db: AsyncSession,
    date_debut: date,
    date_fin: date,
    annee_id: UUID | None = None,
) -> RapportFinancierResponse:
    if annee_id:
        await sync_recettes_paiements(db, annee_id)

    recettes_q = select(func.coalesce(func.sum(EcritureComptable.montant), 0)).where(
        EcritureComptable.type == TypeEcriture.RECETTE.value,
        EcritureComptable.date_ecriture >= date_debut,
        EcritureComptable.date_ecriture <= date_fin,
    )
    depenses_q = select(func.coalesce(func.sum(EcritureComptable.montant), 0)).where(
        EcritureComptable.type == TypeEcriture.DEPENSE.value,
        EcritureComptable.date_ecriture >= date_debut,
        EcritureComptable.date_ecriture <= date_fin,
    )
    total_recettes = Decimal(str((await db.execute(recettes_q)).scalar_one()))
    total_depenses = Decimal(str((await db.execute(depenses_q)).scalar_one()))

    dep_par_cat: dict[str, Decimal] = {}
    dep_cat_result = await db.execute(
        select(CategorieDepense.libelle, func.sum(Depense.montant))
        .join(Depense, Depense.categorie_id == CategorieDepense.id)
        .where(
            Depense.statut == StatutDepense.VALIDEE.value,
            Depense.date_depense >= date_debut,
            Depense.date_depense <= date_fin,
        )
        .group_by(CategorieDepense.libelle)
    )
    for libelle, montant in dep_cat_result.all():
        dep_par_cat[libelle] = Decimal(str(montant))

    recettes_mode: dict[str, Decimal] = {}
    if annee_id:
        pay_result = await db.execute(
            select(Paiement.mode_paiement, func.sum(Paiement.montant)).where(
                Paiement.annee_scolaire_id == annee_id,
                Paiement.statut == StatutPaiement.VALIDE.value,
                Paiement.date_paiement >= date_debut,
                Paiement.date_paiement <= date_fin,
                Paiement.montant > 0,
            ).group_by(Paiement.mode_paiement)
        )
        for mode, montant in pay_result.all():
            recettes_mode[mode] = Decimal(str(montant))

    return RapportFinancierResponse(
        periode_debut=date_debut,
        periode_fin=date_fin,
        total_recettes=total_recettes,
        total_depenses=total_depenses,
        solde=total_recettes - total_depenses,
        recettes_par_mode=recettes_mode,
        depenses_par_categorie=dep_par_cat,
    )


def export_rapport_csv(rapport: RapportFinancierResponse, journal: list[EcritureResponse]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Rapport financier SGEP"])
    writer.writerow(["Période", f"{rapport.periode_debut} → {rapport.periode_fin}"])
    writer.writerow(["Total recettes", str(rapport.total_recettes)])
    writer.writerow(["Total dépenses", str(rapport.total_depenses)])
    writer.writerow(["Solde", str(rapport.solde)])
    writer.writerow([])
    writer.writerow(["Recettes par mode"])
    for mode, montant in rapport.recettes_par_mode.items():
        writer.writerow([mode, str(montant)])
    writer.writerow([])
    writer.writerow(["Dépenses par catégorie"])
    for cat, montant in rapport.depenses_par_categorie.items():
        writer.writerow([cat, str(montant)])
    writer.writerow([])
    writer.writerow(["Journal comptable"])
    writer.writerow(["Date", "Type", "Libellé", "Montant", "Compte"])
    for e in journal:
        writer.writerow([str(e.date_ecriture), e.type, e.libelle, str(e.montant), e.compte_libelle])
    return output.getvalue().encode("utf-8-sig")


async def export_excel_rapport(
    db: AsyncSession,
    date_debut: date,
    date_fin: date,
    annee_id: UUID | None = None,
) -> bytes:
    from io import BytesIO

    from openpyxl import Workbook

    rapport = await get_rapport_financier(db, date_debut, date_fin, annee_id)
    journal = await list_journal(db, date_debut, date_fin)

    wb = Workbook()
    ws = wb.active
    ws.title = "Rapport"
    ws.append(["Période", f"{date_debut} → {date_fin}"])
    ws.append(["Recettes", float(rapport.total_recettes)])
    ws.append(["Dépenses", float(rapport.total_depenses)])
    ws.append(["Solde", float(rapport.solde)])

    ws2 = wb.create_sheet("Journal")
    ws2.append(["Date", "Type", "Libellé", "Montant", "Compte"])
    for e in journal:
        ws2.append([str(e.date_ecriture), e.type, e.libelle, float(e.montant), e.compte_libelle])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()
