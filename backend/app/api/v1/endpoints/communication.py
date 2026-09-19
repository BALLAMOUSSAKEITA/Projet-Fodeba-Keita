from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.communication import (
    AnnonceCreate,
    AnnonceResponse,
    EnvoiMessageCreate,
    HistoriqueResponse,
    ModeleMessageCreate,
    ModeleMessageResponse,
)
from app.services import communication_service

router = APIRouter()

MANAGE_PERMISSION = "communication.manage"
VIEW_PERMISSIONS = ("communication.manage", "communication.view")


@router.get("/annonces", response_model=list[AnnonceResponse])
async def list_annonces(
    audience: str | None = Query(default=None),
    publiees_seulement: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*VIEW_PERMISSIONS)),
):
    return await communication_service.list_annonces(db, audience, publiees_seulement)


@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
async def create_annonce(
    data: AnnonceCreate,
    publier: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MANAGE_PERMISSION)),
):
    return await communication_service.create_annonce(db, data, user.id, publier)


@router.post("/annonces/{annonce_id}/publier", response_model=AnnonceResponse)
async def publier_annonce(
    annonce_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(MANAGE_PERMISSION)),
):
    return await communication_service.publier_annonce(db, annonce_id)


@router.post("/annonces/{annonce_id}/archiver", response_model=AnnonceResponse)
async def archiver_annonce(
    annonce_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(MANAGE_PERMISSION)),
):
    return await communication_service.archiver_annonce(db, annonce_id)


@router.get("/modeles", response_model=list[ModeleMessageResponse])
async def list_modeles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*VIEW_PERMISSIONS)),
):
    return await communication_service.list_modeles(db)


@router.post("/modeles", response_model=ModeleMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_modele(
    data: ModeleMessageCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(MANAGE_PERMISSION)),
):
    return await communication_service.create_modele(db, data)


@router.post("/envoyer", response_model=HistoriqueResponse, status_code=status.HTTP_201_CREATED)
async def envoyer_message(
    data: EnvoiMessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MANAGE_PERMISSION)),
):
    return await communication_service.envoyer_message(db, data, user.id)


@router.get("/historique", response_model=list[HistoriqueResponse])
async def list_historique(
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*VIEW_PERMISSIONS)),
):
    return await communication_service.list_historique(db, limit)
