from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission
from app.models.user import User
from app.schemas.sync import SyncPullResponse, SyncPushRequest, SyncPushResponse
from app.services import sync_service

router = APIRouter()

SYNC_PULL_PERMISSIONS = ("students.view", "grades.modify", "attendance.manage", "payments.collect")
SYNC_PUSH_PERMISSIONS = ("grades.modify", "attendance.manage", "payments.collect")


@router.get("/pull", response_model=SyncPullResponse)
async def sync_pull(
    since: datetime | None = Query(default=None, description="Horodatage ISO pour delta sync"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*SYNC_PULL_PERMISSIONS)),
):
    return await sync_service.pull_offline_bundle(db, since)


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    data: SyncPushRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_any_permission(*SYNC_PUSH_PERMISSIONS)),
):
    return await sync_service.push_batch(
        db,
        data.operations,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_email=user.email,
    )
