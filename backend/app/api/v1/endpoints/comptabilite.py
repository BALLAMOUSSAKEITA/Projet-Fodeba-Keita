from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.comptabilite import (
    BudgetLigneCreate,
    BudgetSuiviResponse,
    CategorieDepenseResponse,
    CompteTresorerieResponse,
    DepenseCreate,
    DepenseRefus,
    DepenseResponse,
    EcritureResponse,
    RapportFinancierResponse,
    TresorerieResponse,
)
from app.services import comptabilite_service

router = APIRouter()

READ_PERMISSIONS = ("expenses.create", "expenses.validate", "reports.view")
CREATE_PERMISSION = "expenses.create"
VALIDATE_PERMISSION = "expenses.validate"


@router.get("/categories", response_model=list[CategorieDepenseResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.list_categories(db)


@router.get("/comptes", response_model=list[CompteTresorerieResponse])
async def list_comptes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.list_comptes_avec_solde(db)


@router.get("/tresorerie", response_model=TresorerieResponse)
async def tresorerie(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.get_tresorerie(db)


@router.get("/depenses", response_model=list[DepenseResponse])
async def list_depenses(
    statut: str | None = Query(default=None),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.list_depenses(db, statut, annee_scolaire_id)


@router.post("/depenses", response_model=DepenseResponse, status_code=status.HTTP_201_CREATED)
async def create_depense(
    data: DepenseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(CREATE_PERMISSION)),
):
    return await comptabilite_service.create_depense(db, data, user.id)


@router.post("/depenses/{depense_id}/soumettre", response_model=DepenseResponse)
async def soumettre_depense(
    depense_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(CREATE_PERMISSION)),
):
    return await comptabilite_service.soumettre_depense(db, depense_id)


@router.post("/depenses/{depense_id}/valider", response_model=DepenseResponse)
async def valider_depense(
    depense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(VALIDATE_PERMISSION)),
):
    return await comptabilite_service.valider_depense(db, depense_id, user.id)


@router.post("/depenses/{depense_id}/refuser", response_model=DepenseResponse)
async def refuser_depense(
    depense_id: UUID,
    data: DepenseRefus,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(VALIDATE_PERMISSION)),
):
    return await comptabilite_service.refuser_depense(db, depense_id, data, user.id)


@router.post("/budget", status_code=status.HTTP_201_CREATED)
async def upsert_budget(
    data: BudgetLigneCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(VALIDATE_PERMISSION)),
):
    ligne = await comptabilite_service.upsert_budget_ligne(db, data)
    return {"id": str(ligne.id), "montant_prevu": str(ligne.montant_prevu)}


@router.get("/budget/suivi", response_model=BudgetSuiviResponse)
async def budget_suivi(
    annee_scolaire_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.get_budget_suivi(db, annee_scolaire_id)


@router.get("/journal", response_model=list[EcritureResponse])
async def journal(
    date_debut: date | None = Query(default=None),
    date_fin: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.list_journal(db, date_debut, date_fin)


@router.get("/rapports/financier", response_model=RapportFinancierResponse)
async def rapport_financier(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_scolaire_id)


@router.get("/export/csv")
async def export_csv(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    rapport = await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_scolaire_id)
    journal = await comptabilite_service.list_journal(db, date_debut, date_fin)
    content = comptabilite_service.export_rapport_csv(rapport, journal)
    return Response(content=content, media_type="text/csv", headers={
        "Content-Disposition": 'attachment; filename="rapport_financier.csv"',
    })


@router.get("/export/excel")
async def export_excel(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    content = await comptabilite_service.export_excel_rapport(db, date_debut, date_fin, annee_scolaire_id)
    return Response(content=content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": 'attachment; filename="rapport_financier.xlsx"',
    })
