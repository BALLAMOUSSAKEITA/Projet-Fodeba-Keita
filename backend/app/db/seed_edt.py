from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emploi_du_temps import CreneauHoraire, SeanceCours
from app.models.parametrage import AnneeScolaire, Classe, Matiere
from app.models.personnel import CategoriePersonnel, Personnel

DEFAULT_CRENEAUX = [
    ("1ère heure", time(8, 0), time(9, 0), 1),
    ("2ème heure", time(9, 0), time(10, 0), 2),
    ("3ème heure", time(10, 15), time(11, 15), 3),
    ("4ème heure", time(11, 15), time(12, 15), 4),
    ("5ème heure", time(14, 0), time(15, 0), 5),
    ("6ème heure", time(15, 0), time(16, 0), 6),
]


async def seed_edt(db: AsyncSession) -> None:
    annee_result = await db.execute(select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)))
    annee = annee_result.scalar_one_or_none()
    if annee is None:
        return

    existing = await db.execute(
        select(CreneauHoraire).where(CreneauHoraire.annee_scolaire_id == annee.id).limit(1)
    )
    if existing.scalar_one_or_none() is not None:
        return

    creneaux: list[CreneauHoraire] = []
    for libelle, debut, fin, ordre in DEFAULT_CRENEAUX:
        c = CreneauHoraire(
            libelle=libelle,
            heure_debut=debut,
            heure_fin=fin,
            ordre=ordre,
            annee_scolaire_id=annee.id,
        )
        db.add(c)
        creneaux.append(c)

    await db.flush()

    enseignant = (
        await db.execute(
            select(Personnel).where(Personnel.categorie == CategoriePersonnel.ENSEIGNANT.value).limit(1)
        )
    ).scalar_one_or_none()
    classe = (await db.execute(select(Classe).limit(1))).scalar_one_or_none()
    matiere = (await db.execute(select(Matiere).where(Matiere.code == "FR"))).scalar_one_or_none()

    if enseignant and classe and matiere and creneaux:
        db.add(
            SeanceCours(
                classe_id=classe.id,
                creneau_id=creneaux[0].id,
                jour_semaine=0,
                matiere_id=matiere.id,
                personnel_id=enseignant.id,
                salle=classe.salle,
                annee_scolaire_id=annee.id,
            )
        )

    await db.flush()
