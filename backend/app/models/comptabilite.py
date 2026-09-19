import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class StatutDepense(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMISE = "soumise"
    VALIDEE = "validee"
    REFUSEE = "refusee"


class TypeCompteTresorerie(str, enum.Enum):
    CAISSE = "caisse"
    BANQUE = "banque"


class TypeEcriture(str, enum.Enum):
    RECETTE = "recette"
    DEPENSE = "depense"


class CategorieDepense(Base, TimestampMixin):
    __tablename__ = "categories_depenses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    actif: Mapped[bool] = mapped_column(default=True, nullable=False)


class Depense(Base, TimestampMixin):
    __tablename__ = "depenses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    categorie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("categories_depenses.id"), nullable=False, index=True
    )
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False, index=True
    )
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date_depense: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    compte_tresorerie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("comptes_tresorerie.id"), nullable=False
    )
    statut: Mapped[str] = mapped_column(String(20), default=StatutDepense.BROUILLON.value, nullable=False)
    saisi_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    valide_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    motif_refus: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_piece: Mapped[str | None] = mapped_column(String(100), nullable=True)


class BudgetLigne(Base, TimestampMixin):
    __tablename__ = "budget_lignes"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "categorie_id", name="uq_budget_annee_categorie"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False
    )
    categorie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("categories_depenses.id", ondelete="CASCADE"), nullable=False
    )
    montant_prevu: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)


class CompteTresorerie(Base, TimestampMixin):
    __tablename__ = "comptes_tresorerie"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    solde_initial: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    actif: Mapped[bool] = mapped_column(default=True, nullable=False)


class EcritureComptable(Base, TimestampMixin):
    __tablename__ = "ecritures_comptables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    date_ecriture: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    compte_tresorerie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("comptes_tresorerie.id"), nullable=False, index=True
    )
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    annee_scolaire_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=True
    )
