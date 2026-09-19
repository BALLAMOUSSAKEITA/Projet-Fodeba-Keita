from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_any_permission, require_permission
from app.models.user import User
from app.schemas.paiements import (
    CaisseJournaliereResponse,
    ImpayeItem,
    PaiementAnnulation,
    PaiementCreate,
    PaiementRemboursement,
    PaiementResponse,
    RelanceCreate,
    RelanceResponse,
    RemiseEleveCreate,
    RemiseEleveResponse,
    SituationEleveResponse,
    TarifNiveauCreate,
    TarifNiveauResponse,
    TrancheFraisCreate,
    TrancheFraisResponse,
)
from app.services import paiements_service

router = APIRouter()

READ_PERMISSIONS = ("payments.collect", "payments.view", "reports.view")
WRITE_PERMISSION = "payments.collect"


@router.get("/tarifs", response_model=list[TarifNiveauResponse])
async def list_tarifs(
    annee_scolaire_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.list_tarifs(db, annee_scolaire_id)


@router.post("/tarifs", response_model=TarifNiveauResponse, status_code=status.HTTP_201_CREATED)
async def create_tarif(
    data: TarifNiveauCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    tarif = await paiements_service.create_tarif(db, data)
    items = await paiements_service.list_tarifs(db, data.annee_scolaire_id)
    return next(i for i in items if i["id"] == tarif.id)


@router.get("/tranches", response_model=list[TrancheFraisResponse])
async def list_tranches(
    annee_scolaire_id: UUID = Query(...),
    type_frais_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.list_tranches(db, annee_scolaire_id, type_frais_id)


@router.post("/tranches", response_model=TrancheFraisResponse, status_code=status.HTTP_201_CREATED)
async def create_tranche(
    data: TrancheFraisCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    tranche = await paiements_service.create_tranche(db, data)
    items = await paiements_service.list_tranches(db, data.annee_scolaire_id, data.type_frais_id)
    return next(i for i in items if i["id"] == tranche.id)


@router.get("/eleve/{eleve_id}/situation", response_model=SituationEleveResponse)
async def situation_eleve(
    eleve_id: UUID,
    annee_scolaire_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.get_situation_eleve(db, eleve_id, annee_scolaire_id)


@router.get("/impayes/liste", response_model=list[ImpayeItem])
async def list_impayes(
    annee_scolaire_id: UUID | None = Query(default=None),
    classe_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.list_impayes(db, annee_scolaire_id, classe_id)


@router.post("/impayes/relance", response_model=RelanceResponse, status_code=status.HTTP_201_CREATED)
async def relancer_impaye(
    data: RelanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paiements_service.create_relance(db, data)


@router.post("/remises", response_model=RemiseEleveResponse, status_code=status.HTTP_201_CREATED)
async def create_remise(
    data: RemiseEleveCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paiements_service.create_remise(db, data)


@router.get("/caisse/journaliere", response_model=CaisseJournaliereResponse)
async def caisse_journaliere(
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.get_caisse_journaliere(db, target_date)


@router.post("", response_model=PaiementResponse, status_code=status.HTTP_201_CREATED)
async def create_paiement(
    data: PaiementCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paiements_service.create_paiement(
        db, data, user.id,
        ip_address=request.client.host if request.client else None,
        user_email=user.email,
    )


@router.get("/{paiement_id}/recu/pdf")
async def recu_pdf(
    paiement_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    pdf = await paiements_service.generate_recu_pdf(db, paiement_id)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="recu_{paiement_id}.pdf"',
    })


@router.post("/{paiement_id}/annuler", response_model=PaiementResponse)
async def annuler_paiement(
    paiement_id: UUID,
    data: PaiementAnnulation,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paiements_service.annuler_paiement(
        db, paiement_id, data, user.id,
        ip_address=request.client.host if request.client else None,
        user_email=user.email,
    )


@router.post("/{paiement_id}/rembourser", response_model=PaiementResponse)
async def rembourser_paiement(
    paiement_id: UUID,
    data: PaiementRemboursement,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(WRITE_PERMISSION)),
):
    return await paiements_service.rembourser_paiement(
        db, paiement_id, data, user.id,
        ip_address=request.client.host if request.client else None,
        user_email=user.email,
    )


@router.get("/{paiement_id}", response_model=PaiementResponse)
async def get_paiement(
    paiement_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await paiements_service.get_paiement(db, paiement_id)
