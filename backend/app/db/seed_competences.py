from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bulletins import Competence
from app.models.parametrage import Niveau, TypeNiveau

COMPETENCES_PS = [
    ("LANG", "Langage", "S'exprimer en phrases simples", 1),
    ("MOTRIC", "Motricité", "Tenir un crayon", 2),
    ("SOCIAL", "Vie sociale", "Jouer avec les autres", 3),
]

COMPETENCES_MS = [
    ("LANG", "Langage", "Réciter comptines", 1),
    ("MOTRIC", "Motricité", "Découper avec ciseaux", 2),
    ("LOGIC", "Logique", "Reconnaître les formes", 3),
]

COMPETENCES_GS = [
    ("LANG", "Langage", "Lire des syllabes", 1),
    ("MOTRIC", "Motricité", "Écrire son prénom", 2),
    ("MATH", "Mathématiques", "Compter jusqu'à 20", 3),
    ("SOCIAL", "Vie sociale", "Respecter les règles", 4),
]


async def seed_competences(db: AsyncSession) -> None:
    existing = await db.execute(select(Competence).limit(1))
    if existing.scalar_one_or_none() is not None:
        return

    niveaux = (
        await db.execute(select(Niveau).where(Niveau.type == TypeNiveau.MATERNELLE.value))
    ).scalars().all()
    mapping = {"PS": COMPETENCES_PS, "MS": COMPETENCES_MS, "GS": COMPETENCES_GS}

    for niveau in niveaux:
        for code, domaine, libelle, ordre in mapping.get(niveau.code, []):
            db.add(
                Competence(
                    code=code,
                    domaine=domaine,
                    libelle=libelle,
                    niveau_id=niveau.id,
                    ordre=ordre,
                )
            )

    await db.flush()
