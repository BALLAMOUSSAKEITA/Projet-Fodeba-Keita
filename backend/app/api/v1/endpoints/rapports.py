from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission
from app.models.user import User
from app.schemas.comptabilite import RapportFinancierResponse
from app.schemas.rapports import (
    DashboardKPIResponse,
    GraphiquesResponse,
    RapportEffectifsResponse,
    RapportPedagogiqueResponse,
    RapportPresenceResponse,
    StatistiquesAnnuellesResponse,
)
from app.services import comptabilite_service, rapports_service

router = APIRouter()

READ_PERMISSIONS = ("reports.view", "reports.view_pedagogical")


@router.get("/dashboard/kpi", response_model=DashboardKPIResponse)
async def dashboard_kpi(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await rapports_service.get_dashboard_kpis(db)


@router.get("/effectifs", response_model=RapportEffectifsResponse)
async def rapport_effectifs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await rapports_service.get_rapport_effectifs(db)


@router.get("/financier", response_model=RapportFinancierResponse)
async def rapport_financier(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("reports.view")),
):
    return await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_scolaire_id)


@router.get("/pedagogique", response_model=RapportPedagogiqueResponse)
async def rapport_pedagogique(
    periode_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await rapports_service.get_rapport_pedagogique(db, periode_id)


@router.get("/presence", response_model=RapportPresenceResponse)
async def rapport_presence(
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await rapports_service.get_rapport_presence(db, date_debut, date_fin)


@router.get("/annuel", response_model=StatistiquesAnnuellesResponse)
async def statistiques_annuelles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("reports.view")),
):
    return await rapports_service.get_statistiques_annuelles(db)


@router.get("/graphiques", response_model=GraphiquesResponse)
async def graphiques(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await rapports_service.get_graphiques(db)


@router.get("/export/csv")
async def export_csv(
    type: str = Query(..., pattern=r"^(effectifs|financier)$"),
    date_debut: date | None = Query(default=None),
    date_fin: date | None = Query(default=None),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("reports.view")),
):
    if type == "effectifs":
        rapport = await rapports_service.get_rapport_effectifs(db)
        content = rapports_service.export_csv_effectifs(rapport)
        filename = "rapport_effectifs.csv"
    else:
        if not date_debut or not date_fin:
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="date_debut et date_fin requis")
        rapport = await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_scolaire_id)
        journal = await comptabilite_service.list_journal(db, date_debut, date_fin)
        content = comptabilite_service.export_rapport_csv(rapport, journal)
        filename = "rapport_financier.csv"

    return Response(content=content, media_type="text/csv", headers={
        "Content-Disposition": f'attachment; filename="{filename}"',
    })


@router.get("/export/excel")
async def export_excel(
    type: str = Query(..., pattern=r"^(effectifs|financier|pedagogique|annuel)$"),
    date_debut: date | None = Query(default=None),
    date_fin: date | None = Query(default=None),
    annee_scolaire_id: UUID | None = Query(default=None),
    periode_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("reports.view")),
):
    annee = annee_scolaire_id
    if type == "financier" and not date_debut:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="date_debut et date_fin requis")
    content = await rapports_service.export_excel_rapport(
        db,
        type,
        date_debut=date_debut,
        date_fin=date_fin,
        annee_id=annee,
        periode_id=periode_id,
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="rapport_{type}.xlsx"'},
    )


@router.get("/export/pdf")
async def export_pdf(
    type: str = Query(..., pattern=r"^(effectifs|financier|annuel)$"),
    date_debut: date | None = Query(default=None),
    date_fin: date | None = Query(default=None),
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("reports.view")),
):
    if type == "financier" and (not date_debut or not date_fin):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="date_debut et date_fin requis")
    content = await rapports_service.export_pdf_rapport(
        db,
        type,
        date_debut=date_debut,
        date_fin=date_fin,
        annee_id=annee_scolaire_id,
    )
    return Response(content=content, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="rapport_{type}.pdf"',
    })
