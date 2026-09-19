from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_any_permission, require_permission
from app.models.user import User
from app.schemas.notes import (
    EvaluationCreate,
    EvaluationResponse,
    GrilleNotesResponse,
    MoyennesClasseResponse,
    NotesBulkUpdate,
    TypeEvaluationCreate,
    TypeEvaluationResponse,
    ValidationResponse,
)
from app.services import notes_service

router = APIRouter()

READ_PERMISSIONS = ("grades.modify", "grades.validate_bulletins", "reports.view_pedagogical")


@router.get("/types-evaluation", response_model=list[TypeEvaluationResponse])
async def list_types(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await notes_service.list_types_evaluation(db)


@router.post("/types-evaluation", response_model=TypeEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_type(
    data: TypeEvaluationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("grades.validate_bulletins")),
):
    return await notes_service.create_type_evaluation(db, data)


@router.get("/evaluations", response_model=list[EvaluationResponse])
async def list_evaluations(
    classe_id: UUID = Query(...),
    matiere_id: UUID = Query(...),
    periode_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await notes_service.list_evaluations(db, classe_id, matiere_id, periode_id)


@router.post("/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("grades.modify")),
):
    return await notes_service.create_evaluation(db, data)


@router.get("/evaluations/{evaluation_id}/grille", response_model=GrilleNotesResponse)
async def get_grille(
    evaluation_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await notes_service.get_grille_notes(db, evaluation_id)


@router.put("/evaluations/{evaluation_id}/notes", response_model=GrilleNotesResponse)
async def update_notes(
    evaluation_id: UUID,
    data: NotesBulkUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("grades.modify")),
):
    return await notes_service.bulk_update_notes(
        db,
        evaluation_id,
        data,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_email=user.email,
    )


@router.get("/classes/{classe_id}/periodes/{periode_id}/moyennes", response_model=MoyennesClasseResponse)
async def moyennes_classe(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await notes_service.get_moyennes_classe(db, classe_id, periode_id)


@router.post("/classes/{classe_id}/periodes/{periode_id}/valider", response_model=ValidationResponse)
async def valider_notes(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("grades.validate_bulletins")),
):
    return await notes_service.valider_periode(db, classe_id, periode_id, current_user.id)


@router.post("/classes/{classe_id}/periodes/{periode_id}/deverrouiller", response_model=ValidationResponse)
async def deverrouiller_notes(
    classe_id: UUID,
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("grades.validate_bulletins")),
):
    return await notes_service.valider_periode(
        db, classe_id, periode_id, current_user.id, verrouiller=False
    )
