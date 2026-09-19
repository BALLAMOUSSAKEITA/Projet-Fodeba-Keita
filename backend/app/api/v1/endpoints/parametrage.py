from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.parametrage import (
    AnneeScolaireCreate,
    AnneeScolaireResponse,
    AnneeScolaireUpdate,
    BaremeResponse,
    BaremeUpdate,
    CalendrierCreate,
    CalendrierResponse,
    CalendrierUpdate,
    ClasseCreate,
    ClasseResponse,
    ClasseUpdate,
    EtablissementResponse,
    EtablissementUpdate,
    MatiereCreate,
    MatiereResponse,
    MatiereUpdate,
    NiveauCreate,
    NiveauResponse,
    NiveauUpdate,
    ParametrageStatutResponse,
    PeriodeCreate,
    PeriodeResponse,
    PeriodeUpdate,
    ReferentielResponse,
    TypeFraisCreate,
    TypeFraisResponse,
    TypeFraisUpdate,
)
from app.services import parametrage_service as svc

router = APIRouter()


@router.get("/statut", response_model=ParametrageStatutResponse)
async def get_statut(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.get_parametrage_statut(db)


@router.get("/etablissement", response_model=EtablissementResponse)
async def get_etablissement(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    etab = await svc.get_etablissement(db)
    if etab is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Établissement non configuré")
    return etab


@router.patch("/etablissement", response_model=EtablissementResponse)
async def update_etablissement(
    data: EtablissementUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_etablissement(db, data)


@router.get("/annees-scolaires", response_model=list[AnneeScolaireResponse])
async def list_annees(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_annees(db)


@router.get("/annees-scolaires/active", response_model=AnneeScolaireResponse)
async def get_annee_active(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    annee = await svc.get_annee_active(db)
    if annee is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Aucune année scolaire active")
    return annee


@router.post("/annees-scolaires", response_model=AnneeScolaireResponse, status_code=status.HTTP_201_CREATED)
async def create_annee(
    data: AnneeScolaireCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_annee(db, data)


@router.patch("/annees-scolaires/{annee_id}", response_model=AnneeScolaireResponse)
async def update_annee(
    annee_id: UUID,
    data: AnneeScolaireUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_annee(db, annee_id, data)


@router.post("/annees-scolaires/{annee_id}/activer", response_model=AnneeScolaireResponse)
async def activer_annee(
    annee_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.activer_annee(db, annee_id)


@router.get("/niveaux", response_model=list[NiveauResponse])
async def list_niveaux(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_niveaux(db)


@router.post("/niveaux", response_model=NiveauResponse, status_code=status.HTTP_201_CREATED)
async def create_niveau(
    data: NiveauCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_niveau(db, data)


@router.patch("/niveaux/{niveau_id}", response_model=NiveauResponse)
async def update_niveau(
    niveau_id: UUID,
    data: NiveauUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_niveau(db, niveau_id, data)


@router.get("/classes", response_model=list[ClasseResponse])
async def list_classes(
    annee_scolaire_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_classes(db, annee_scolaire_id)


@router.post("/classes", response_model=ClasseResponse, status_code=status.HTTP_201_CREATED)
async def create_classe(
    data: ClasseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_classe(db, data)


@router.patch("/classes/{classe_id}", response_model=ClasseResponse)
async def update_classe(
    classe_id: UUID,
    data: ClasseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_classe(db, classe_id, data)


@router.get("/matieres", response_model=list[MatiereResponse])
async def list_matieres(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_matieres(db)


@router.post("/matieres", response_model=MatiereResponse, status_code=status.HTTP_201_CREATED)
async def create_matiere(
    data: MatiereCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_matiere(db, data)


@router.patch("/matieres/{matiere_id}", response_model=MatiereResponse)
async def update_matiere(
    matiere_id: UUID,
    data: MatiereUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_matiere(db, matiere_id, data)


@router.get("/periodes", response_model=list[PeriodeResponse])
async def list_periodes(
    annee_scolaire_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_periodes(db, annee_scolaire_id)


@router.post("/periodes", response_model=PeriodeResponse, status_code=status.HTTP_201_CREATED)
async def create_periode(
    data: PeriodeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_periode(db, data)


@router.patch("/periodes/{periode_id}", response_model=PeriodeResponse)
async def update_periode(
    periode_id: UUID,
    data: PeriodeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_periode(db, periode_id, data)


@router.get("/bareme/{annee_id}", response_model=BaremeResponse)
async def get_bareme(
    annee_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.get_bareme(db, annee_id)


@router.patch("/bareme/{annee_id}", response_model=BaremeResponse)
async def update_bareme(
    annee_id: UUID,
    data: BaremeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_bareme(db, annee_id, data)


@router.get("/types-frais", response_model=list[TypeFraisResponse])
async def list_types_frais(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_types_frais(db)


@router.post("/types-frais", response_model=TypeFraisResponse, status_code=status.HTTP_201_CREATED)
async def create_type_frais(
    data: TypeFraisCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_type_frais(db, data)


@router.patch("/types-frais/{type_id}", response_model=TypeFraisResponse)
async def update_type_frais(
    type_id: UUID,
    data: TypeFraisUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_type_frais(db, type_id, data)


@router.get("/calendrier", response_model=list[CalendrierResponse])
async def list_calendrier(
    annee_scolaire_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_calendrier(db, annee_scolaire_id)


@router.post("/calendrier", response_model=CalendrierResponse, status_code=status.HTTP_201_CREATED)
async def create_calendrier(
    data: CalendrierCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.create_calendrier(db, data)


@router.patch("/calendrier/{entry_id}", response_model=CalendrierResponse)
async def update_calendrier(
    entry_id: UUID,
    data: CalendrierUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("settings.manage")),
):
    return await svc.update_calendrier(db, entry_id, data)


@router.get("/referentiels/{ref_type}", response_model=list[ReferentielResponse])
async def list_referentiels(
    ref_type: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await svc.list_referentiels(db, ref_type)
