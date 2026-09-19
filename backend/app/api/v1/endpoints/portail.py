from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.user import User
from app.schemas.communication import EnfantItem, PortailResumeResponse
from app.services import portail_service

router = APIRouter()

PORTAIL_PERMISSION = "parent.portal"


@router.get("/mes-enfants", response_model=list[EnfantItem])
async def mes_enfants(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PORTAIL_PERMISSION)),
):
    return await portail_service.list_mes_enfants(db, user.id)


@router.get("/enfants/{eleve_id}/resume", response_model=PortailResumeResponse)
async def resume_enfant(
    eleve_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PORTAIL_PERMISSION)),
):
    return await portail_service.get_resume_enfant(db, user.id, eleve_id)
