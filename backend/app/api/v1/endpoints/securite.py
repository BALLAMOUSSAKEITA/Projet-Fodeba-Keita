from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.login_log import LoginLog
from app.models.user import User
from app.schemas.auth import LoginLogResponse
from app.schemas.securite import (
    AuditLogResponse,
    HistoriqueNoteResponse,
    HistoriquePaiementResponse,
    SauvegardeStatusResponse,
)
from app.services import audit_service, parametrage_service, securite_service

router = APIRouter()

AUDIT_PERMISSION = "security.audit"


@router.get("/audit", response_model=list[AuditLogResponse])
async def list_audit(
    limit: int = Query(default=100, ge=1, le=500),
    resource_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(AUDIT_PERMISSION)),
):
    return await audit_service.list_audit_logs(db, limit, resource_type, action)


@router.get("/historique/notes", response_model=list[HistoriqueNoteResponse])
async def historique_notes(
    eleve_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(AUDIT_PERMISSION)),
):
    return await audit_service.list_historique_notes(db, eleve_id, limit)


@router.get("/historique/paiements", response_model=list[HistoriquePaiementResponse])
async def historique_paiements(
    eleve_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(AUDIT_PERMISSION)),
):
    return await audit_service.list_historique_paiements(db, eleve_id, limit)


@router.get("/connexions", response_model=list[LoginLogResponse])
async def connexions(
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(AUDIT_PERMISSION)),
):
    result = await db.execute(
        select(LoginLog).order_by(LoginLog.created_at.desc()).limit(min(limit, 200))
    )
    return list(result.scalars().all())


@router.get("/sauvegarde", response_model=SauvegardeStatusResponse)
async def sauvegarde_status(
    _: User = Depends(require_permission(AUDIT_PERMISSION)),
):
    return securite_service.get_sauvegarde_status()


@router.post("/annees/{annee_id}/cloturer")
async def cloturer_annee(
    annee_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("settings.manage")),
):
    annee = await parametrage_service.cloturer_annee(db, annee_id)
    await audit_service.log_audit(
        db,
        action="cloture",
        resource_type="annee_scolaire",
        resource_id=str(annee_id),
        details=f"Clôture année {annee.libelle}",
        user_id=user.id,
        user_email=user.email,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    return {"id": str(annee.id), "libelle": annee.libelle, "statut": annee.statut}
