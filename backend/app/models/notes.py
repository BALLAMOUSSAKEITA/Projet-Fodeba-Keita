import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class TypeEvaluation(Base, TimestampMixin):
    __tablename__ = "types_evaluation"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "code", name="uq_type_eval_annee_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    coefficient_defaut: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=1, nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="type_evaluation")


class Evaluation(Base, TimestampMixin):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    classe_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("classes.id"), nullable=False)
    matiere_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("matieres.id"), nullable=False)
    periode_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("periodes.id"), nullable=False)
    type_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("types_evaluation.id"), nullable=False
    )
    coefficient: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=1, nullable=False)
    date_evaluation: Mapped[date | None] = mapped_column(Date, nullable=True)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    type_evaluation: Mapped[TypeEvaluation] = relationship(back_populates="evaluations")
    notes: Mapped[list["Note"]] = relationship(back_populates="evaluation", cascade="all, delete-orphan")


class Note(Base, TimestampMixin):
    __tablename__ = "notes"
    __table_args__ = (
        UniqueConstraint("evaluation_id", "eleve_id", name="uq_note_evaluation_eleve"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=False)
    valeur: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_absent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    appreciation_libre: Mapped[str | None] = mapped_column(Text, nullable=True)
    appreciation_auto: Mapped[str | None] = mapped_column(String(100), nullable=True)

    evaluation: Mapped[Evaluation] = relationship(back_populates="notes")


class ValidationPeriode(Base, TimestampMixin):
    __tablename__ = "validations_periode"
    __table_args__ = (
        UniqueConstraint("classe_id", "periode_id", name="uq_validation_classe_periode"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    classe_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("classes.id"), nullable=False)
    periode_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("periodes.id"), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )
    verrouille: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    valide_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    date_validation: Mapped[date | None] = mapped_column(Date, nullable=True)
