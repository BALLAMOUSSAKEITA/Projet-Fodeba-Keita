import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class StatutPeriodePaie(str, enum.Enum):
    OUVERTE = "ouverte"
    CLOTUREE = "cloturee"


class StatutBulletinPaie(str, enum.Enum):
    BROUILLON = "brouillon"
    VALIDE = "valide"
    PAYE = "paye"


class StatutAvance(str, enum.Enum):
    ACTIVE = "active"
    REMBOURSEE = "remboursee"


class PeriodePaie(Base, TimestampMixin):
    __tablename__ = "periodes_paie"
    __table_args__ = (UniqueConstraint("annee", "mois", name="uq_periode_paie_annee_mois"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutPeriodePaie.OUVERTE.value, nullable=False)


class BulletinPaie(Base, TimestampMixin):
    __tablename__ = "bulletins_paie"
    __table_args__ = (UniqueConstraint("personnel_id", "periode_paie_id", name="uq_bulletin_personnel_periode"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True
    )
    periode_paie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("periodes_paie.id", ondelete="CASCADE"), nullable=False, index=True
    )
    salaire_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    prime_anciennete: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    prime_autre: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    indemnite_transport: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    indemnite_logement: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    retenue_cnss: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    retenue_its: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    retenue_absences: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    retenue_avances: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    autres_retenues: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"), nullable=False)
    brut: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    net_a_payer: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    jours_absence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutBulletinPaie.BROUILLON.value, nullable=False)
    paye_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class AvanceSalaire(Base, TimestampMixin):
    __tablename__ = "avances_salaire"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    personnel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False, index=True
    )
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date_avance: Mapped[date] = mapped_column(Date, nullable=False)
    motif: Mapped[str | None] = mapped_column(Text, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default=StatutAvance.ACTIVE.value, nullable=False)
    bulletin_paie_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("bulletins_paie.id", ondelete="SET NULL"), nullable=True
    )
