import enum
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class ActionAudit(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    CLOTURE = "cloture"
    ANNULATION = "annulation"


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)


class HistoriqueNote(Base, TimestampMixin):
    __tablename__ = "historique_notes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=False, index=True)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("annees_scolaires.id"), nullable=False)
    ancienne_valeur: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    nouvelle_valeur: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    ancien_absent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    nouveau_absent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    modifie_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)


class HistoriquePaiement(Base, TimestampMixin):
    __tablename__ = "historique_paiements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    paiement_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("paiements.id"), nullable=False, index=True)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=False, index=True)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("annees_scolaires.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut_avant: Mapped[str | None] = mapped_column(String(20), nullable=True)
    statut_apres: Mapped[str] = mapped_column(String(20), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    modifie_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
