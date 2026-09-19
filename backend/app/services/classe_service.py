from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.eleve import Eleve, Inscription, StatutEleve
from app.models.parametrage import Classe, Niveau
from app.schemas.classe import ClasseEffectifResponse, ClasseElevesResponse, EleveClasseItem
from app.services import parametrage_service


async def count_classe_effectif(db: AsyncSession, classe_id: UUID, annee_id: UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Inscription)
        .where(
            Inscription.classe_id == classe_id,
            Inscription.annee_scolaire_id == annee_id,
            Inscription.statut == StatutEleve.ACTIF.value,
        )
    )
    return result.scalar_one()


async def get_classe_effectifs(db: AsyncSession, annee_id: UUID | None = None) -> list[ClasseEffectifResponse]:
    annee = await parametrage_service.get_annee_active(db) if not annee_id else await parametrage_service._get_annee(db, annee_id)
    if annee is None:
        return []

    result = await db.execute(
        select(Classe)
        .options(selectinload(Classe.niveau))
        .where(Classe.annee_scolaire_id == annee.id)
        .order_by(Classe.nom)
    )
    classes = list(result.scalars().all())
    items: list[ClasseEffectifResponse] = []

    for classe in classes:
        effectif = await count_classe_effectif(db, classe.id, annee.id)
        places = max(classe.capacite_max - effectif, 0)
        items.append(
            ClasseEffectifResponse(
                id=classe.id,
                nom=classe.nom,
                niveau_code=classe.niveau.code,
                niveau_libelle=classe.niveau.libelle,
                capacite_max=classe.capacite_max,
                effectif=effectif,
                places_restantes=places,
                depassement=effectif > classe.capacite_max,
                salle=classe.salle,
            )
        )
    return items


async def list_eleves_classe(db: AsyncSession, classe_id: UUID) -> ClasseElevesResponse:
    result = await db.execute(
        select(Classe).options(selectinload(Classe.niveau)).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    annee = await parametrage_service.get_annee_active(db)
    query = (
        select(Eleve)
        .join(Inscription, Inscription.eleve_id == Eleve.id)
        .where(
            Inscription.classe_id == classe_id,
            Eleve.statut == StatutEleve.ACTIF.value,
        )
        .order_by(Eleve.nom, Eleve.prenoms)
    )
    if annee:
        query = query.where(Inscription.annee_scolaire_id == annee.id)

    eleves_result = await db.execute(query)
    eleves = list(eleves_result.scalars().all())

    return ClasseElevesResponse(
        classe=classe,
        effectif=len(eleves),
        capacite_max=classe.capacite_max,
        eleves=[
            EleveClasseItem(
                id=e.id,
                matricule=e.matricule,
                nom=e.nom,
                prenoms=e.prenoms,
                sexe=e.sexe,
                date_naissance=str(e.date_naissance),
            )
            for e in eleves
        ],
    )


async def verify_capacity(db: AsyncSession, classe_id: UUID, annee_id: UUID) -> Classe:
    result = await db.execute(
        select(Classe).options(selectinload(Classe.niveau)).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    effectif = await count_classe_effectif(db, classe_id, annee_id)
    if effectif >= classe.capacite_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Capacité maximale atteinte ({classe.capacite_max} élèves)",
        )
    return classe
