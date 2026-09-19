import enum
import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Sexe(str, enum.Enum):
    M = "M"
    F = "F"


class StatutEleve(str, enum.Enum):
    ACTIF = "actif"
    INACTIF = "inactif"


class TypeInscription(str, enum.Enum):
    NOUVELLE = "nouvelle"
    REINSCRIPTION = "reinscription"


class TypeTuteur(str, enum.Enum):
    PERE = "pere"
    MERE = "mere"
    TUTEUR = "tuteur"


class Eleve(Base, TimestampMixin):
    __tablename__ = "eleves"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    matricule: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prenoms: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    sexe: Mapped[str] = mapped_column(String(1), nullable=False)
    date_naissance: Mapped[date] = mapped_column(Date, nullable=False)
    lieu_naissance: Mapped[str | None] = mapped_column(String(150), nullable=True)
    nationalite: Mapped[str | None] = mapped_column(String(50), nullable=True)
    adresse: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    groupe_sanguin: Mapped[str | None] = mapped_column(String(10), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutEleve.ACTIF.value, nullable=False)
    motif_inactivite: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_inactivite: Mapped[date | None] = mapped_column(Date, nullable=True)

    tuteurs: Mapped[list["Tuteur"]] = relationship(
        back_populates="eleve",
        cascade="all, delete-orphan",
    )
    inscriptions: Mapped[list["Inscription"]] = relationship(
        back_populates="eleve",
        cascade="all, delete-orphan",
    )
    transferts: Mapped[list["Transfert"]] = relationship(
        back_populates="eleve",
        cascade="all, delete-orphan",
    )


class Tuteur(Base, TimestampMixin):
    __tablename__ = "tuteurs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenoms: Mapped[str] = mapped_column(String(150), nullable=False)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False)
    profession: Mapped[str | None] = mapped_column(String(100), nullable=True)
    adresse: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    eleve: Mapped[Eleve] = relationship(back_populates="tuteurs")


class Inscription(Base, TimestampMixin):
    __tablename__ = "inscriptions"
    __table_args__ = (
        UniqueConstraint("eleve_id", "annee_scolaire_id", name="uq_inscription_eleve_annee"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )
    niveau_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("niveaux.id"), nullable=False)
    classe_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("classes.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    date_inscription: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutEleve.ACTIF.value, nullable=False)

    eleve: Mapped[Eleve] = relationship(back_populates="inscriptions")
    niveau: Mapped["Niveau"] = relationship()
    annee_scolaire: Mapped["AnneeScolaire"] = relationship()
    classe: Mapped["Classe | None"] = relationship()


class TypeTransfert(str, enum.Enum):
    ENTRANT = "entrant"
    SORTANT = "sortant"


class Transfert(Base, TimestampMixin):
    __tablename__ = "transferts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    ecole: Mapped[str] = mapped_column(String(255), nullable=False)
    date_transfert: Mapped[date] = mapped_column(Date, nullable=False)
    motif: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    eleve: Mapped[Eleve] = relationship(back_populates="transferts")


from app.models.parametrage import AnneeScolaire, Classe, Niveau  # noqa: E402
