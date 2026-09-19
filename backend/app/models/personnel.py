import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class CategoriePersonnel(str, enum.Enum):
    ENSEIGNANT = "enseignant"
    NON_ENSEIGNANT = "non_enseignant"


class StatutPersonnel(str, enum.Enum):
    ACTIF = "actif"
    INACTIF = "inactif"


class TypeContrat(str, enum.Enum):
    CDI = "cdi"
    CDD = "cdd"
    VACATAIRE = "vacataire"


class StatutContrat(str, enum.Enum):
    ACTIF = "actif"
    TERMINE = "termine"


class TypeConge(str, enum.Enum):
    CONGE = "conge"
    MALADIE = "maladie"
    PERMISSION = "permission"
    ABSENCE = "absence"


class StatutConge(str, enum.Enum):
    DEMANDE = "demande"
    APPROUVE = "approuve"
    REFUSE = "refuse"


class Personnel(Base, TimestampMixin):
    __tablename__ = "personnel"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    matricule: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prenoms: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    sexe: Mapped[str] = mapped_column(String(1), nullable=False)
    date_naissance: Mapped[date | None] = mapped_column(Date, nullable=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    adresse: Mapped[str | None] = mapped_column(String(500), nullable=True)
    categorie: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    fonction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    specialite: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_embauche: Mapped[date | None] = mapped_column(Date, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutPersonnel.ACTIF.value, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )

    diplomes: Mapped[list["Diplome"]] = relationship(
        back_populates="personnel",
        cascade="all, delete-orphan",
    )
    contrats: Mapped[list["Contrat"]] = relationship(
        back_populates="personnel",
        cascade="all, delete-orphan",
    )
    affectations: Mapped[list["AffectationPedagogique"]] = relationship(
        back_populates="personnel",
        cascade="all, delete-orphan",
    )
    conges: Mapped[list["CongeAbsence"]] = relationship(
        back_populates="personnel",
        cascade="all, delete-orphan",
    )


class Diplome(Base, TimestampMixin):
    __tablename__ = "diplomes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False
    )
    libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    etablissement: Mapped[str | None] = mapped_column(String(200), nullable=True)
    annee_obtention: Mapped[int | None] = mapped_column(nullable=True)
    niveau: Mapped[str | None] = mapped_column(String(100), nullable=True)

    personnel: Mapped[Personnel] = relationship(back_populates="diplomes")


class Contrat(Base, TimestampMixin):
    __tablename__ = "contrats"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False
    )
    type_contrat: Mapped[str] = mapped_column(String(20), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    salaire_mensuel: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutContrat.ACTIF.value, nullable=False)

    personnel: Mapped[Personnel] = relationship(back_populates="contrats")


class AffectationPedagogique(Base, TimestampMixin):
    __tablename__ = "affectations_pedagogiques"
    __table_args__ = (
        UniqueConstraint(
            "personnel_id",
            "classe_id",
            "matiere_id",
            "annee_scolaire_id",
            name="uq_affectation_personnel_classe_matiere_annee",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False
    )
    classe_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("classes.id"), nullable=False)
    matiere_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("matieres.id"), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    personnel: Mapped[Personnel] = relationship(back_populates="affectations")
    classe: Mapped["Classe"] = relationship("Classe")
    matiere: Mapped["Matiere"] = relationship("Matiere")


class CongeAbsence(Base, TimestampMixin):
    __tablename__ = "conges_absences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    motif: Mapped[str | None] = mapped_column(Text, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutConge.DEMANDE.value, nullable=False)

    personnel: Mapped[Personnel] = relationship(back_populates="conges")
