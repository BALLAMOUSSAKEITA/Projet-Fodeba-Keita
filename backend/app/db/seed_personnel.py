from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parametrage import Classe, Matiere
from app.models.personnel import (
    AffectationPedagogique,
    CategoriePersonnel,
    Contrat,
    Diplome,
    Personnel,
    TypeContrat,
)
from app.models.user import User


async def seed_personnel(db: AsyncSession) -> None:
    result = await db.execute(select(Personnel).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    user_result = await db.execute(
        select(User).where(User.email == "enseignant@fodebakeita.gn")
    )
    enseignant_user = user_result.scalar_one_or_none()

    enseignant = Personnel(
        matricule="ENS-0001",
        nom="Diallo",
        prenoms="Mamadou",
        sexe="M",
        date_naissance=date(1985, 3, 15),
        telephone="+224620000003",
        email="enseignant@fodebakeita.gn",
        categorie=CategoriePersonnel.ENSEIGNANT.value,
        specialite="Enseignement primaire",
        date_embauche=date(2020, 9, 1),
        statut="actif",
        user_id=enseignant_user.id if enseignant_user else None,
    )
    db.add(enseignant)

    secretaire = Personnel(
        matricule="PER-0001",
        nom="Camara",
        prenoms="Fatoumata",
        sexe="F",
        telephone="+224620000010",
        email="secretaire@fodebakeita.gn",
        categorie=CategoriePersonnel.NON_ENSEIGNANT.value,
        fonction="Secrétaire de direction",
        date_embauche=date(2021, 1, 10),
        statut="actif",
    )
    db.add(secretaire)

    gardien = Personnel(
        matricule="PER-0002",
        nom="Bah",
        prenoms="Ibrahima",
        sexe="M",
        telephone="+224620000011",
        categorie=CategoriePersonnel.NON_ENSEIGNANT.value,
        fonction="Agent de sécurité",
        date_embauche=date(2019, 6, 1),
        statut="actif",
    )
    db.add(gardien)

    await db.flush()

    db.add(
        Diplome(
            personnel_id=enseignant.id,
            libelle="Licence en Sciences de l'Éducation",
            etablissement="Université Gamal Abdel Nasser",
            annee_obtention=2010,
            niveau="Licence",
        )
    )
    db.add(
        Contrat(
            personnel_id=enseignant.id,
            type_contrat=TypeContrat.CDI.value,
            date_debut=date(2020, 9, 1),
            salaire_mensuel=3500000,
            statut="actif",
        )
    )

    classe_result = await db.execute(select(Classe).limit(1))
    classe = classe_result.scalar_one_or_none()
    matiere_result = await db.execute(select(Matiere).where(Matiere.code == "FR"))
    matiere = matiere_result.scalar_one_or_none()

    if classe and matiere:
        db.add(
            AffectationPedagogique(
                personnel_id=enseignant.id,
                classe_id=classe.id,
                matiere_id=matiere.id,
                annee_scolaire_id=classe.annee_scolaire_id,
            )
        )
        classe.titulaire_id = enseignant.id

    await db.flush()
