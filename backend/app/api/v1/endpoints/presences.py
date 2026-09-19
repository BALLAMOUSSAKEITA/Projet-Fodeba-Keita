from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.presences import (
    AppelBulkUpdate,
    AppelPresenceResponse,
    ClasseRecapResponse,
    EleveRecapResponse,
    EnseignantAbsenceItem,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    JustificationReview,
    JustificationUpdate,
    PresenceEleveRow,
)
from app.services import presences_service

router = APIRouter()

READ_PERMISSIONS = ("attendance.manage", "attendance.view", "students.view")
WRITE_PERMISSION = "attendance.manage"


@router.get("/classes/{classe_id}/appels", response_model=AppelPresenceResponse)
async def get_appel(
    classe_id: UUID,
    date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.get_appel(db, classe_id, date)


@router.put("/classes/{classe_id}/appels", response_model=AppelPresenceResponse)
async def save_appel(
    classe_id: UUID,
    date: date = Query(..., alias="date"),
    data: AppelBulkUpdate = ...,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await presences_service.save_appel(db, classe_id, date, data, user.id)


@router.post("/presences/{presence_id}/justification", response_model=PresenceEleveRow)
async def submit_justification(
    presence_id: UUID,
    data: JustificationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.submit_justification(db, presence_id, data)


@router.patch("/presences/{presence_id}/justification", response_model=PresenceEleveRow)
async def review_justification(
    presence_id: UUID,
    data: JustificationReview,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await presences_service.review_justification(db, presence_id, data)


@router.get("/classes/{classe_id}/recapitulatif", response_model=ClasseRecapResponse)
async def classe_recap(
    classe_id: UUID,
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.get_classe_recap(db, classe_id, date_debut, date_fin)


@router.get("/eleve/{eleve_id}/recapitulatif", response_model=EleveRecapResponse)
async def eleve_recap(
    eleve_id: UUID,
    date_debut: date = Query(...),
    date_fin: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.get_eleve_recap(db, eleve_id, date_debut, date_fin)


@router.get("/enseignants/absences", response_model=list[EnseignantAbsenceItem])
async def enseignants_absences(
    date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.list_enseignants_absences(db, date)


@router.get("/absences-a-justifier", response_model=list[PresenceEleveRow])
async def absences_a_justifier(
    classe_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.list_absences_a_justifier(db, classe_id)


@router.get("/discipline", response_model=list[IncidentResponse])
async def list_incidents(
    classe_id: UUID | None = Query(default=None),
    eleve_id: UUID | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await presences_service.list_incidents(db, classe_id, eleve_id, skip, limit)


@router.post("/discipline", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await presences_service.create_incident(db, data, user.id)


@router.patch("/discipline/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await presences_service.update_incident(db, incident_id, data)
