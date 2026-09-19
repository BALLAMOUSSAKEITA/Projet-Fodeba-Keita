from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.bulletins import (
    CompetenceBulkUpdate,
    CompetenceGrilleResponse,
    CompetenceResponse,
    DecisionPassageCreate,
    DecisionPassageResponse,
    PalmaresResponse,
    StatsPedagogiquesResponse,
)
from app.services import bulletin_service

router = APIRouter()

READ_PERMISSIONS = ("grades.validate_bulletins", "grades.modify", "reports.view_pedagogical")


@router.get("/eleve/{eleve_id}/periodes/{periode_id}/pdf")
async def bulletin_eleve_pdf(
    eleve_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    pdf = await bulletin_service.generate_bulletin_pdf(db, eleve_id, periode_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="bulletin_{eleve_id}.pdf"',
    })


@router.get("/classes/{classe_id}/periodes/{periode_id}/pdf")
async def bulletins_classe_pdf(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    pdf = await bulletin_service.generate_bulletins_classe_pdf(db, classe_id, periode_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="bulletins_classe_{classe_id}.pdf"',
    })


@router.get("/eleve/{eleve_id}/annuel/pdf")
async def bulletin_annuel_pdf(
    eleve_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    pdf = await bulletin_service.generate_bulletin_annuel_pdf(db, eleve_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="bulletin_annuel_{eleve_id}.pdf"',
    })


@router.get("/classes/{classe_id}/periodes/{periode_id}/stats", response_model=StatsPedagogiquesResponse)
async def stats_pedagogiques(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await bulletin_service.get_stats_pedagogiques(db, classe_id, periode_id)


@router.get("/classes/{classe_id}/periodes/{periode_id}/palmares", response_model=PalmaresResponse)
async def palmares(
    classe_id: UUID,
    periode_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await bulletin_service.get_palmares(db, classe_id, periode_id, limit)


@router.post("/decisions-passage", response_model=DecisionPassageResponse, status_code=201)
async def create_decision(
    data: DecisionPassageCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("grades.validate_bulletins")),
):
    return await bulletin_service.set_decision_passage(db, data)


@router.get("/competences", response_model=list[CompetenceResponse])
async def list_competences(
    niveau_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    comps = await bulletin_service.list_competences(db, niveau_id)
    return [CompetenceResponse.model_validate(c) for c in comps]


@router.get("/classes/{classe_id}/periodes/{periode_id}/competences", response_model=CompetenceGrilleResponse)
async def grille_competences(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await bulletin_service.get_grille_competences(db, classe_id, periode_id)


@router.put("/classes/{classe_id}/periodes/{periode_id}/competences", response_model=CompetenceGrilleResponse)
async def update_competences(
    classe_id: UUID,
    periode_id: UUID,
    items: list[CompetenceBulkUpdate],
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("grades.modify")),
):
    return await bulletin_service.bulk_update_competences(db, periode_id, items)


@router.get("/eleve/{eleve_id}/periodes/{periode_id}/maternelle/pdf")
async def bulletin_maternelle_pdf(
    eleve_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    pdf = await bulletin_service.generate_bulletin_maternelle_pdf(db, eleve_id, periode_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="bulletin_maternelle_{eleve_id}.pdf"',
    })
