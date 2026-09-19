from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.paie import (
    AvanceSalaireCreate,
    AvanceSalaireResponse,
    BulletinPaieResponse,
    BulletinPaieUpdate,
    MasseSalarialeResponse,
    PeriodePaieCreate,
    PeriodePaieResponse,
)
from app.services import paie_service

router = APIRouter()

READ_PERMISSIONS = ("payroll.generate", "payroll.view", "reports.view", "grades.view_own")
WRITE_PERMISSION = "payroll.generate"


@router.get("/periodes", response_model=list[PeriodePaieResponse])
async def list_periodes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paie_service.list_periodes(db)


@router.post("/periodes", response_model=PeriodePaieResponse, status_code=status.HTTP_201_CREATED)
async def create_periode(
    data: PeriodePaieCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paie_service.create_periode(db, data)


@router.post("/periodes/{periode_id}/generer", response_model=list[BulletinPaieResponse])
async def generer_paie(
    periode_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paie_service.generer_paie_mensuelle(db, periode_id)


@router.get("/bulletins", response_model=list[BulletinPaieResponse])
async def list_bulletins(
    periode_paie_id: UUID | None = Query(default=None),
    personnel_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paie_service.list_bulletins(db, periode_paie_id, personnel_id)


@router.get("/mes-bulletins", response_model=list[BulletinPaieResponse])
async def mes_bulletins(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_any_permission(*READ_PERMISSIONS, "grades.view_own")),
):
    return await paie_service.get_mes_bulletins(db, user.id)


@router.get("/masse-salariale", response_model=MasseSalarialeResponse)
async def masse_salariale(
    periode_paie_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paie_service.get_masse_salariale(db, periode_paie_id)


@router.get("/avances", response_model=list[AvanceSalaireResponse])
async def list_avances(
    personnel_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paie_service.list_avances(db, personnel_id)


@router.post("/avances", response_model=AvanceSalaireResponse, status_code=status.HTTP_201_CREATED)
async def create_avance(
    data: AvanceSalaireCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    avance = await paie_service.create_avance(db, data)
    items = await paie_service.list_avances(db, data.personnel_id)
    return next(i for i in items if i["id"] == avance.id)


@router.get("/bulletins/{bulletin_id}", response_model=BulletinPaieResponse)
async def get_bulletin(
    bulletin_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paie_service.get_bulletin(db, bulletin_id)


@router.get("/bulletins/{bulletin_id}/pdf")
async def bulletin_pdf(
    bulletin_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS, "grades.view_own")),
):
    pdf = await paie_service.generate_bulletin_pdf(db, bulletin_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="bulletin_paie_{bulletin_id}.pdf"',
    })


@router.patch("/bulletins/{bulletin_id}", response_model=BulletinPaieResponse)
async def update_bulletin(
    bulletin_id: UUID,
    data: BulletinPaieUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paie_service.update_bulletin(db, bulletin_id, data)


@router.post("/bulletins/{bulletin_id}/valider", response_model=BulletinPaieResponse)
async def valider_bulletin(
    bulletin_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paie_service.valider_bulletin(db, bulletin_id)


@router.post("/bulletins/{bulletin_id}/payer", response_model=BulletinPaieResponse)
async def payer_bulletin(
    bulletin_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paie_service.payer_bulletin(db, bulletin_id, user.id)
