from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_any_permission, require_permission
from app.models.user import User
from app.schemas.eleve import (
    AffecterClasseRequest,
    DesactiverEleveRequest,
    EffectifStatsResponse,
    EleveCreate,
    EleveListResponse,
    EleveResponse,
    EleveUpdate,
    HistoriqueScolaireResponse,
    ReinscriptionRequest,
    TransfertEntrantCreate,
    TransfertSortantRequest,
    TuteurCreate,
    TuteurUpdate,
)
from app.services import eleve_service, parametrage_service, pdf_service

router = APIRouter()

READ_PERMISSIONS = ("students.view", "students.enroll", "reports.view_pedagogical")


@router.get("/statistiques/effectifs", response_model=EffectifStatsResponse)
async def stats_effectifs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await eleve_service.get_stats_effectifs(db)


@router.post("/transfert-entrant", response_model=EleveResponse, status_code=status.HTTP_201_CREATED)
async def transfert_entrant(
    data: TransfertEntrantCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.create_transfert_entrant(db, data)


@router.get("", response_model=EleveListResponse)
async def list_eleves(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    sexe: str | None = Query(None, pattern=r"^(M|F)$"),
    niveau_id: UUID | None = Query(None),
    classe_id: UUID | None = Query(None),
    statut: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    items, total = await eleve_service.list_eleves(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sexe=sexe,
        niveau_id=niveau_id,
        classe_id=classe_id,
        statut=statut,
    )
    return EleveListResponse(items=items, total=total)


@router.post("", response_model=EleveResponse, status_code=status.HTTP_201_CREATED)
async def create_eleve(
    data: EleveCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.create_eleve(db, data)


@router.get("/{eleve_id}/historique", response_model=HistoriqueScolaireResponse)
async def historique_eleve(
    eleve_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await eleve_service.get_historique(db, eleve_id)


@router.get("/{eleve_id}/attestation/scolarite")
async def attestation_scolarite(
    eleve_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    eleve = await eleve_service.get_eleve(db, eleve_id)
    etab = await parametrage_service.get_etablissement(db)
    annee = await parametrage_service.get_annee_active(db)
    pdf_bytes = pdf_service.generate_attestation_scolarite(
        eleve, etab, annee.libelle if annee else "—"
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="attestation_{eleve.matricule}.pdf"'},
    )


@router.get("/{eleve_id}/attestation/transfert")
async def certificat_transfert(
    eleve_id: UUID,
    ecole: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    eleve = await eleve_service.get_eleve(db, eleve_id)
    etab = await parametrage_service.get_etablissement(db)
    pdf_bytes = pdf_service.generate_certificat_transfert(eleve, etab, ecole)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="transfert_{eleve.matricule}.pdf"'},
    )


@router.get("/{eleve_id}", response_model=EleveResponse)
async def get_eleve(
    eleve_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await eleve_service.get_eleve(db, eleve_id)


@router.patch("/{eleve_id}", response_model=EleveResponse)
async def update_eleve(
    eleve_id: UUID,
    data: EleveUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.update_eleve(db, eleve_id, data)


@router.post("/{eleve_id}/affecter-classe", response_model=EleveResponse)
async def affecter_classe(
    eleve_id: UUID,
    data: AffecterClasseRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.affecter_classe(db, eleve_id, data.classe_id)


@router.post("/{eleve_id}/reinscrire", response_model=EleveResponse)
async def reinscrire_eleve(
    eleve_id: UUID,
    data: ReinscriptionRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.reinscrire_eleve(db, eleve_id, data)


@router.post("/{eleve_id}/transfert-sortant", response_model=EleveResponse)
async def transfert_sortant(
    eleve_id: UUID,
    data: TransfertSortantRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.transfert_sortant(db, eleve_id, data)


@router.post("/{eleve_id}/desactiver", response_model=EleveResponse)
async def desactiver_eleve(
    eleve_id: UUID,
    data: DesactiverEleveRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.desactiver_eleve(
        db, eleve_id, data.motif, data.date_inactivite
    )


@router.post("/{eleve_id}/tuteurs", response_model=EleveResponse, status_code=status.HTTP_201_CREATED)
async def add_tuteur(
    eleve_id: UUID,
    data: TuteurCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.add_tuteur(db, eleve_id, data)


@router.patch("/{eleve_id}/tuteurs/{tuteur_id}", response_model=EleveResponse)
async def update_tuteur(
    eleve_id: UUID,
    tuteur_id: UUID,
    data: TuteurUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.update_tuteur(db, eleve_id, tuteur_id, data)


@router.delete("/{eleve_id}/tuteurs/{tuteur_id}", response_model=EleveResponse)
async def delete_tuteur(
    eleve_id: UUID,
    tuteur_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("students.enroll")),
):
    return await eleve_service.delete_tuteur(db, eleve_id, tuteur_id)
