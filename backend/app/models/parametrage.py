import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

matiere_niveaux = Table(
    "matiere_niveaux",
    Base.metadata,
    Column("matiere_id", Uuid, ForeignKey("matieres.id", ondelete="CASCADE"), primary_key=True),
    Column("niveau_id", Uuid, ForeignKey("niveaux.id", ondelete="CASCADE"), primary_key=True),
    Column("coefficient", Numeric(4, 2), nullable=False, default=1),
)


class StatutAnneeScolaire(str, enum.Enum):
    PLANIFIEE = "planifiee"
    ACTIVE = "active"
    CLOTUREE = "cloturee"


class TypeNiveau(str, enum.Enum):
    MATERNELLE = "maternelle"
    PRIMAIRE = "primaire"


class TypePeriode(str, enum.Enum):
    TRIMESTRE = "trimestre"
    SEMESTRE = "semestre"


class EchelleNotation(str, enum.Enum):
    SUR_10 = "/10"
    SUR_20 = "/20"
    SUR_100 = "/100"


class TypeCalendrier(str, enum.Enum):
    FERIE = "ferie"
    VACANCE = "vacance"
    EXCEPTION = "exception"


class Etablissement(Base, TimestampMixin):
    __tablename__ = "etablissements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    adresse: Mapped[str | None] = mapped_column(String(500), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prefecture: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commune: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    devise_principale: Mapped[str] = mapped_column(String(10), default="GNF", nullable=False)
    devise_secondaire: Mapped[str | None] = mapped_column(String(10), nullable=True)


class AnneeScolaire(Base, TimestampMixin):
    __tablename__ = "annees_scolaires"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    libelle: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutAnneeScolaire.PLANIFIEE.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    periodes: Mapped[list["Periode"]] = relationship(back_populates="annee_scolaire")
    classes: Mapped[list["Classe"]] = relationship(back_populates="annee_scolaire")
    bareme: Mapped["Bareme | None"] = relationship(back_populates="annee_scolaire", uselist=False)


class Niveau(Base, TimestampMixin):
    __tablename__ = "niveaux"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    classes: Mapped[list["Classe"]] = relationship(back_populates="niveau")
    matieres: Mapped[list["Matiere"]] = relationship(
        secondary=matiere_niveaux,
        back_populates="niveaux",
    )


class Classe(Base, TimestampMixin):
    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "niveau_id", "nom", name="uq_classe_annee_niveau_nom"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(50), nullable=False)
    capacite_max: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    salle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    niveau_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("niveaux.id"), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )
    titulaire_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="SET NULL"), nullable=True
    )

    niveau: Mapped[Niveau] = relationship(back_populates="classes")
    annee_scolaire: Mapped[AnneeScolaire] = relationship(back_populates="classes")


class Matiere(Base, TimestampMixin):
    __tablename__ = "matieres"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    coefficient_defaut: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=1, nullable=False)

    niveaux: Mapped[list[Niveau]] = relationship(
        secondary=matiere_niveaux,
        back_populates="matieres",
    )


class Periode(Base, TimestampMixin):
    __tablename__ = "periodes"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "ordre", name="uq_periode_annee_ordre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(20), default=TypePeriode.TRIMESTRE.value)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    annee_scolaire: Mapped[AnneeScolaire] = relationship(back_populates="periodes")


class Bareme(Base, TimestampMixin):
    __tablename__ = "baremes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), unique=True, nullable=False
    )
    echelle: Mapped[str] = mapped_column(String(10), default=EchelleNotation.SUR_20.value)
    arrondi_decimales: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    seuil_passage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=10, nullable=False)
    seuil_redoublement: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=8, nullable=False)

    annee_scolaire: Mapped[AnneeScolaire] = relationship(back_populates="bareme")


class TypeFrais(Base, TimestampMixin):
    __tablename__ = "types_frais"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CalendrierScolaire(Base, TimestampMixin):
    __tablename__ = "calendrier_scolaire"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )


class Referentiel(Base, TimestampMixin):
    __tablename__ = "referentiels"
    __table_args__ = (
        UniqueConstraint("type", "code", name="uq_referentiel_type_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("referentiels.id"), nullable=True
    )
