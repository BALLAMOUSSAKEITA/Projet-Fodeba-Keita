from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notes import TypeEvaluation
from app.models.parametrage import AnneeScolaire

DEFAULT_TYPES = [
    ("DEV", "Devoir", Decimal("1")),
    ("COMP", "Composition", Decimal("2")),
    ("INTERRO", "Interrogation", Decimal("1")),
]


async def seed_notes(db: AsyncSession) -> None:
    annee = (
        await db.execute(select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)))
    ).scalar_one_or_none()
    if annee is None:
        return

    existing = await db.execute(
        select(TypeEvaluation).where(TypeEvaluation.annee_scolaire_id == annee.id).limit(1)
    )
    if existing.scalar_one_or_none() is not None:
        return

    for code, libelle, coef in DEFAULT_TYPES:
        db.add(
            TypeEvaluation(
                code=code,
                libelle=libelle,
                coefficient_defaut=coef,
                annee_scolaire_id=annee.id,
            )
        )

    await db.flush()
