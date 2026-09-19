import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ModePaiement(str, enum.Enum):
    ESPECES = "especes"
    ORANGE_MONEY = "orange_money"
    MTN_MOMO = "mtn_momo"
    VIREMENT = "virement"
    CHEQUE = "cheque"


class StatutPaiement(str, enum.Enum):
    VALIDE = "valide"
    ANNULE = "annule"
    REMBOURSE = "rembourse"


class TarifNiveau(Base, TimestampMixin):
    __tablename__ = "tarifs_niveaux"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "niveau_id", "type_frais_id", name="uq_tarif_annee_niveau_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False, index=True
    )
    niveau_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("niveaux.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_frais_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("types_frais.id", ondelete="CASCADE"), nullable=False, index=True
    )
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


class TrancheFrais(Base, TimestampMixin):
    __tablename__ = "tranches_frais"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "type_frais_id", "ordre", name="uq_tranche_annee_type_ordre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_frais_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("types_frais.id", ondelete="CASCADE"), nullable=False, index=True
    )
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    date_echeance: Mapped[date] = mapped_column(Date, nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    pourcentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


class RemiseEleve(Base, TimestampMixin):
    __tablename__ = "remises_eleves"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False, index=True
    )
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_frais_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("types_frais.id", ondelete="SET NULL"), nullable=True
    )
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    pourcentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    motif: Mapped[str] = mapped_column(String(255), nullable=False)


class Paiement(Base, TimestampMixin):
    __tablename__ = "paiements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False, index=True
    )
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_frais_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("types_frais.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tranche_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("tranches_frais.id", ondelete="SET NULL"), nullable=True
    )
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    remise_montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    mode_paiement: Mapped[str] = mapped_column(String(20), nullable=False)
    reference_externe: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_paiement: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    numero_recu: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutPaiement.VALIDE.value, nullable=False)
    encaisse_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    paiement_origine_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("paiements.id", ondelete="SET NULL"), nullable=True
    )
    motif_annulation: Mapped[str | None] = mapped_column(Text, nullable=True)
    libelle: Mapped[str | None] = mapped_column(String(255), nullable=True)


class RelanceImpaye(Base, TimestampMixin):
    __tablename__ = "relances_impayes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False, index=True
    )
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), nullable=False
    )
    tranche_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("tranches_frais.id", ondelete="SET NULL"), nullable=True
    )
    date_relance: Mapped[date] = mapped_column(Date, nullable=False)
    canal: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)


class SequenceRecu(Base):
    __tablename__ = "sequences_recu"

    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id", ondelete="CASCADE"), primary_key=True
    )
    dernier_numero: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
