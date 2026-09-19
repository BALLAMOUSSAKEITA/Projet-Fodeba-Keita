from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.communication import Annonce, AudienceAnnonce, ModeleMessage, StatutAnnonce
from app.models.eleve import Eleve, Inscription, Tuteur, TypeInscription
from app.models.parametrage import AnneeScolaire, Niveau
from app.models.role import Role
from app.models.user import User

MODELES = [
    ("RELANCE_IMPAYE", "Relance impayé scolarité", "Relance scolarité", "Bonjour, votre solde scolarité présente un reste à payer. Merci de régulariser.", "sms"),
    ("REUNION_PARENTS", "Convocation réunion parents", "Réunion parents d'élèves", "Vous êtes convoqué(e) à la réunion des parents le {date} à {heure}.", "sms"),
    ("ABSENCE_ALERTE", "Alerte absence", "Absence de votre enfant", "Votre enfant a été absent(e) aujourd'hui sans justification.", "app"),
]

ANNONCES = [
    ("Rentrée scolaire 2025-2026", "La rentrée des classes est fixée au lundi 6 octobre. Accueil à 7h30.", AudienceAnnonce.TOUS.value),
    ("Réunion parents — CP", "Réunion d'information pour les parents de CP le vendredi 15 novembre à 16h.", AudienceAnnonce.PARENTS.value),
]


async def seed_communication(db: AsyncSession) -> None:
    existing = await db.execute(select(ModeleMessage).limit(1))
    if existing.scalar_one_or_none() is not None:
        return

    for code, libelle, sujet, corps, canal in MODELES:
        db.add(ModeleMessage(code=code, libelle=libelle, sujet=sujet, corps=corps, canal=canal, actif=True))
    await db.flush()

    role_result = await db.execute(select(Role).where(Role.code == "parent"))
    parent_role = role_result.scalar_one_or_none()

    parent_user = None
    if parent_role:
        user_result = await db.execute(select(User).where(User.email == "parent@fodebakeita.gn"))
        parent_user = user_result.scalar_one_or_none()
        if parent_user is None:
            parent_user = User(
                email="parent@fodebakeita.gn",
                password_hash=hash_password("parent123"),
                nom="Camara",
                prenom="Aissatou",
                telephone="+224623333333",
                role_id=parent_role.id,
                is_active=True,
            )
            db.add(parent_user)
            await db.flush()

    annee_result = await db.execute(
        select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)).limit(1)
    )
    annee = annee_result.scalar_one_or_none()

    eleve_result = await db.execute(select(Eleve).limit(1))
    eleve = eleve_result.scalar_one_or_none()

    if eleve is None and annee and parent_user:
        niveau_result = await db.execute(
            select(Niveau).where(Niveau.code == "3A").limit(1)
        )
        niveau = niveau_result.scalar_one_or_none()
        if niveau:
            eleve = Eleve(
                matricule="2025-P3-0001",
                nom="Camara",
                prenoms="Fatoumata",
                sexe="F",
                date_naissance=date(2016, 7, 20),
                lieu_naissance="Conakry",
                nationalite="Guinéenne",
            )
            db.add(eleve)
            await db.flush()
            db.add(
                Inscription(
                    eleve_id=eleve.id,
                    annee_scolaire_id=annee.id,
                    niveau_id=niveau.id,
                    type=TypeInscription.NOUVELLE.value,
                    date_inscription=date.today(),
                    statut="actif",
                )
            )
            db.add(
                Tuteur(
                    eleve_id=eleve.id,
                    type="mere",
                    nom="Camara",
                    prenoms="Aissatou",
                    telephone="+224623333333",
                    email="parent@fodebakeita.gn",
                    user_id=parent_user.id,
                )
            )
            await db.flush()

    if parent_user and eleve:
        tuteur_result = await db.execute(
            select(Tuteur).where(Tuteur.eleve_id == eleve.id, Tuteur.user_id.is_(None)).limit(1)
        )
        tuteur = tuteur_result.scalar_one_or_none()
        if tuteur:
            tuteur.user_id = parent_user.id

    admin_result = await db.execute(select(User).where(User.email == "admin@fodebakeita.gn"))
    admin = admin_result.scalar_one_or_none()

    for titre, contenu, audience in ANNONCES:
        db.add(
            Annonce(
                titre=titre,
                contenu=contenu,
                audience=audience,
                statut=StatutAnnonce.PUBLIEE.value,
                date_publication=date.today(),
                auteur_id=admin.id if admin else None,
                annee_scolaire_id=annee.id if annee else None,
            )
        )

    await db.flush()
