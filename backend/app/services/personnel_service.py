from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.parametrage import Classe
from app.models.personnel import (
    AffectationPedagogique,
    CategoriePersonnel,
    CongeAbsence,
    Contrat,
    Diplome,
    Personnel,
)
from app.schemas.personnel import (
    AffectationCreate,
    CongeCreate,
    CongeUpdate,
    ContratCreate,
    ContratUpdate,
    DiplomeCreate,
    DiplomeUpdate,
    PersonnelCreate,
    PersonnelListItem,
    PersonnelUpdate,
)
from app.services import parametrage_service

MATRICULE_PREFIX = {
    CategoriePersonnel.ENSEIGNANT.value: "ENS",
    CategoriePersonnel.NON_ENSEIGNANT.value: "PER",
}


async def generate_matricule(db: AsyncSession, categorie: str) -> str:
    prefix = MATRICULE_PREFIX.get(categorie, "PER")
    pattern = f"{prefix}-%"

    result = await db.execute(
        select(Personnel.matricule)
        .where(Personnel.matricule.like(pattern))
        .order_by(Personnel.matricule.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    seq = int(last.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{seq:04d}"


def _personnel_query_options():
    return (
        selectinload(Personnel.diplomes),
        selectinload(Personnel.contrats),
        selectinload(Personnel.conges),
        selectinload(Personnel.affectations).selectinload(AffectationPedagogique.classe),
        selectinload(Personnel.affectations).selectinload(AffectationPedagogique.matiere),
    )


async def get_personnel(db: AsyncSession, personnel_id: UUID) -> Personnel:
    result = await db.execute(
        select(Personnel)
        .options(*_personnel_query_options())
        .where(Personnel.id == personnel_id)
        .execution_options(populate_existing=True)
    )
    personnel = result.scalar_one_or_none()
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel introuvable")

    titulaire_result = await db.execute(
        select(Classe).where(Classe.titulaire_id == personnel_id)
    )
    personnel.classes_titulaire = list(titulaire_result.scalars().all())  # type: ignore[attr-defined]
    return personnel


async def list_personnel(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    categorie: str | None = None,
    statut: str | None = None,
) -> tuple[list[PersonnelListItem], int]:
    query = select(Personnel)
    count_query = select(func.count()).select_from(Personnel)

    if search:
        pattern = f"%{search}%"
        filt = or_(
            Personnel.nom.ilike(pattern),
            Personnel.prenoms.ilike(pattern),
            Personnel.matricule.ilike(pattern),
        )
        query = query.where(filt)
        count_query = count_query.where(filt)

    if categorie:
        query = query.where(Personnel.categorie == categorie)
        count_query = count_query.where(Personnel.categorie == categorie)

    if statut:
        query = query.where(Personnel.statut == statut)
        count_query = count_query.where(Personnel.statut == statut)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(
        query.order_by(Personnel.nom, Personnel.prenoms).offset(skip).limit(limit)
    )
    items = [
        PersonnelListItem.model_validate(p)
        for p in result.scalars().all()
    ]
    return items, total


async def create_personnel(db: AsyncSession, data: PersonnelCreate) -> Personnel:
    if data.categorie == CategoriePersonnel.NON_ENSEIGNANT.value and not data.fonction:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fonction est requise pour le personnel non enseignant",
        )

    matricule = await generate_matricule(db, data.categorie)
    personnel = Personnel(matricule=matricule, **data.model_dump())
    db.add(personnel)
    await db.commit()
    return await get_personnel(db, personnel.id)


async def update_personnel(
    db: AsyncSession,
    personnel_id: UUID,
    data: PersonnelUpdate,
) -> Personnel:
    personnel = await get_personnel(db, personnel_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(personnel, field, value)
    await db.commit()
    return await get_personnel(db, personnel_id)


async def add_diplome(
    db: AsyncSession,
    personnel_id: UUID,
    data: DiplomeCreate,
) -> Personnel:
    await get_personnel(db, personnel_id)
    db.add(Diplome(personnel_id=personnel_id, **data.model_dump()))
    await db.commit()
    return await get_personnel(db, personnel_id)


async def update_diplome(
    db: AsyncSession,
    personnel_id: UUID,
    diplome_id: UUID,
    data: DiplomeUpdate,
) -> Personnel:
    result = await db.execute(
        select(Diplome).where(Diplome.id == diplome_id, Diplome.personnel_id == personnel_id)
    )
    diplome = result.scalar_one_or_none()
    if diplome is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diplôme introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(diplome, field, value)
    await db.commit()
    return await get_personnel(db, personnel_id)


async def delete_diplome(db: AsyncSession, personnel_id: UUID, diplome_id: UUID) -> Personnel:
    result = await db.execute(
        select(Diplome).where(Diplome.id == diplome_id, Diplome.personnel_id == personnel_id)
    )
    diplome = result.scalar_one_or_none()
    if diplome is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diplôme introuvable")
    await db.delete(diplome)
    await db.commit()
    return await get_personnel(db, personnel_id)


async def add_contrat(
    db: AsyncSession,
    personnel_id: UUID,
    data: ContratCreate,
) -> Personnel:
    await get_personnel(db, personnel_id)
    db.add(Contrat(personnel_id=personnel_id, **data.model_dump()))
    await db.commit()
    return await get_personnel(db, personnel_id)


async def update_contrat(
    db: AsyncSession,
    personnel_id: UUID,
    contrat_id: UUID,
    data: ContratUpdate,
) -> Personnel:
    result = await db.execute(
        select(Contrat).where(Contrat.id == contrat_id, Contrat.personnel_id == personnel_id)
    )
    contrat = result.scalar_one_or_none()
    if contrat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrat introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contrat, field, value)
    await db.commit()
    return await get_personnel(db, personnel_id)


async def add_affectation(
    db: AsyncSession,
    personnel_id: UUID,
    data: AffectationCreate,
) -> Personnel:
    personnel = await get_personnel(db, personnel_id)
    if personnel.categorie != CategoriePersonnel.ENSEIGNANT.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Seuls les enseignants peuvent avoir des affectations pédagogiques",
        )

    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Aucune année active")

    annee_id = data.annee_scolaire_id or annee.id

    classe = await db.get(Classe, data.classe_id)
    if classe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classe introuvable")

    from app.models.parametrage import Matiere

    matiere = await db.get(Matiere, data.matiere_id)
    if matiere is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matière introuvable")

    db.add(
        AffectationPedagogique(
            personnel_id=personnel_id,
            classe_id=data.classe_id,
            matiere_id=data.matiere_id,
            annee_scolaire_id=annee_id,
        )
    )
    try:
        await db.flush()
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Affectation déjà existante pour cette classe et matière",
        ) from None
    db.expire_all()
    return await get_personnel(db, personnel_id)


async def delete_affectation(
    db: AsyncSession,
    personnel_id: UUID,
    affectation_id: UUID,
) -> Personnel:
    result = await db.execute(
        select(AffectationPedagogique).where(
            AffectationPedagogique.id == affectation_id,
            AffectationPedagogique.personnel_id == personnel_id,
        )
    )
    affectation = result.scalar_one_or_none()
    if affectation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Affectation introuvable")
    await db.delete(affectation)
    await db.commit()
    return await get_personnel(db, personnel_id)


async def set_titulaire(
    db: AsyncSession,
    personnel_id: UUID,
    classe_id: UUID,
) -> Personnel:
    personnel = await get_personnel(db, personnel_id)
    if personnel.categorie != CategoriePersonnel.ENSEIGNANT.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Seul un enseignant peut être titulaire de classe",
        )

    classe = await db.get(Classe, classe_id)
    if classe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classe introuvable")

    old_classes = (
        await db.execute(select(Classe).where(Classe.titulaire_id == personnel_id))
    ).scalars().all()
    for old in old_classes:
        if old.id != classe_id:
            old.titulaire_id = None

    if classe.titulaire_id and classe.titulaire_id != personnel_id:
        pass  # remplace l'ancien titulaire

    classe.titulaire_id = personnel_id
    await db.commit()
    return await get_personnel(db, personnel_id)


async def add_conge(
    db: AsyncSession,
    personnel_id: UUID,
    data: CongeCreate,
) -> Personnel:
    if data.date_fin < data.date_debut:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de fin doit être postérieure à la date de début",
        )
    await get_personnel(db, personnel_id)
    db.add(CongeAbsence(personnel_id=personnel_id, **data.model_dump()))
    await db.commit()
    return await get_personnel(db, personnel_id)


async def update_conge(
    db: AsyncSession,
    personnel_id: UUID,
    conge_id: UUID,
    data: CongeUpdate,
) -> Personnel:
    result = await db.execute(
        select(CongeAbsence).where(
            CongeAbsence.id == conge_id,
            CongeAbsence.personnel_id == personnel_id,
        )
    )
    conge = result.scalar_one_or_none()
    if conge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Congé introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conge, field, value)
    if conge.date_fin < conge.date_debut:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de fin doit être postérieure à la date de début",
        )
    await db.commit()
    return await get_personnel(db, personnel_id)
