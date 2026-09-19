from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.personnel import (
    AffectationCreate,
    CongeCreate,
    CongeUpdate,
    ContratCreate,
    ContratUpdate,
    DiplomeCreate,
    DiplomeUpdate,
    PersonnelCreate,
    PersonnelListResponse,
    PersonnelResponse,
    PersonnelUpdate,
    TitulaireRequest,
)
from app.services import personnel_service

router = APIRouter()

READ_PERMISSIONS = ("personnel.view", "personnel.manage", "users.manage")


@router.get("", response_model=PersonnelListResponse)
async def list_personnel(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    categorie: str | None = Query(None, pattern=r"^(enseignant|non_enseignant)$"),
    statut: str | None = Query(None, pattern=r"^(actif|inactif)$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    items, total = await personnel_service.list_personnel(
        db, skip=skip, limit=limit, search=search, categorie=categorie, statut=statut
    )
    return PersonnelListResponse(items=items, total=total)


@router.post("", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
async def create_personnel(
    data: PersonnelCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.create_personnel(db, data)


@router.get("/{personnel_id}", response_model=PersonnelResponse)
async def get_personnel(
    personnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await personnel_service.get_personnel(db, personnel_id)


@router.patch("/{personnel_id}", response_model=PersonnelResponse)
async def update_personnel(
    personnel_id: UUID,
    data: PersonnelUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.update_personnel(db, personnel_id, data)


@router.post("/{personnel_id}/diplomes", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
async def add_diplome(
    personnel_id: UUID,
    data: DiplomeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.add_diplome(db, personnel_id, data)


@router.patch("/{personnel_id}/diplomes/{diplome_id}", response_model=PersonnelResponse)
async def update_diplome(
    personnel_id: UUID,
    diplome_id: UUID,
    data: DiplomeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.update_diplome(db, personnel_id, diplome_id, data)


@router.delete("/{personnel_id}/diplomes/{diplome_id}", response_model=PersonnelResponse)
async def delete_diplome(
    personnel_id: UUID,
    diplome_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.delete_diplome(db, personnel_id, diplome_id)


@router.post("/{personnel_id}/contrats", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
async def add_contrat(
    personnel_id: UUID,
    data: ContratCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.add_contrat(db, personnel_id, data)


@router.patch("/{personnel_id}/contrats/{contrat_id}", response_model=PersonnelResponse)
async def update_contrat(
    personnel_id: UUID,
    contrat_id: UUID,
    data: ContratUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.update_contrat(db, personnel_id, contrat_id, data)


@router.post("/{personnel_id}/affectations", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
async def add_affectation(
    personnel_id: UUID,
    data: AffectationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.add_affectation(db, personnel_id, data)


@router.delete("/{personnel_id}/affectations/{affectation_id}", response_model=PersonnelResponse)
async def delete_affectation(
    personnel_id: UUID,
    affectation_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.delete_affectation(db, personnel_id, affectation_id)


@router.post("/{personnel_id}/titulaire", response_model=PersonnelResponse)
async def set_titulaire(
    personnel_id: UUID,
    data: TitulaireRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.set_titulaire(db, personnel_id, data.classe_id)


@router.post("/{personnel_id}/conges", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
async def add_conge(
    personnel_id: UUID,
    data: CongeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission("personnel.manage", "personnel.view")),
):
    return await personnel_service.add_conge(db, personnel_id, data)


@router.patch("/{personnel_id}/conges/{conge_id}", response_model=PersonnelResponse)
async def update_conge(
    personnel_id: UUID,
    conge_id: UUID,
    data: CongeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("personnel.manage")),
):
    return await personnel_service.update_conge(db, personnel_id, conge_id, data)
