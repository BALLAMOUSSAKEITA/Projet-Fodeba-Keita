from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.emploi_du_temps import (
    ConflitsListResponse,
    CreneauCreate,
    CreneauResponse,
    CreneauUpdate,
    GrilleEdtResponse,
    SeanceCreate,
    SeanceResponse,
    SeanceUpdate,
)
from app.services import edt_service, parametrage_service, pdf_service

router = APIRouter()

READ_PERMISSIONS = ("timetable.view", "timetable.manage", "reports.view_pedagogical")


@router.get("/creneaux", response_model=list[CreneauResponse])
async def list_creneaux(
    annee_scolaire_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await edt_service.list_creneaux(db, annee_scolaire_id)


@router.post("/creneaux", response_model=CreneauResponse, status_code=201)
async def create_creneau(
    data: CreneauCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    return await edt_service.create_creneau(db, data)


@router.patch("/creneaux/{creneau_id}", response_model=CreneauResponse)
async def update_creneau(
    creneau_id: UUID,
    data: CreneauUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    return await edt_service.update_creneau(db, creneau_id, data)


@router.delete("/creneaux/{creneau_id}", status_code=204)
async def delete_creneau(
    creneau_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    await edt_service.delete_creneau(db, creneau_id)


@router.get("/conflits", response_model=ConflitsListResponse)
async def list_conflits(
    annee_scolaire_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await edt_service.list_conflits(db, annee_scolaire_id)


@router.get("/classe/{classe_id}", response_model=GrilleEdtResponse)
async def grille_classe(
    classe_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await edt_service.get_grille_classe(db, classe_id)


@router.get("/classe/{classe_id}/export/pdf")
async def export_classe_pdf(
    classe_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    grille = await edt_service.get_grille_classe(db, classe_id)
    etab = await parametrage_service.get_etablissement(db)
    pdf_bytes = pdf_service.generate_edt_pdf(grille.titre, grille.jours, grille.lignes, etab)
    filename = f"edt_classe_{classe_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/classe/{classe_id}/export/excel")
async def export_classe_excel(
    classe_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    grille = await edt_service.get_grille_classe(db, classe_id)
    xlsx_bytes = edt_service.generate_edt_excel(grille)
    filename = f"edt_classe_{classe_id}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/enseignant/{personnel_id}", response_model=GrilleEdtResponse)
async def grille_enseignant(
    personnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await edt_service.get_grille_enseignant(db, personnel_id)


@router.post("/seances", response_model=SeanceResponse, status_code=201)
async def create_seance(
    data: SeanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    return await edt_service.create_seance(db, data)


@router.patch("/seances/{seance_id}", response_model=SeanceResponse)
async def update_seance(
    seance_id: UUID,
    data: SeanceUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    return await edt_service.update_seance(db, seance_id, data)


@router.delete("/seances/{seance_id}", status_code=204)
async def delete_seance(
    seance_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("timetable.manage")),
):
    await edt_service.delete_seance(db, seance_id)
