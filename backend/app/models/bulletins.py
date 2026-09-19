import enum
import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class DecisionPassageEnum(str, enum.Enum):
    ADMIS = "admis"
    REDOUBLE = "redouble"
    EXCLU = "exclu"


class StatutCompetence(str, enum.Enum):
    ACQUIS = "acquis"
    EN_COURS = "en_cours"
    NON_ACQUIS = "non_acquis"


class Competence(Base, TimestampMixin):
    __tablename__ = "competences"
    __table_args__ = (
        UniqueConstraint("niveau_id", "code", name="uq_competence_niveau_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    domaine: Mapped[str] = mapped_column(String(100), nullable=False)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    niveau_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("niveaux.id"), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    evaluations: Mapped[list["EvaluationCompetence"]] = relationship(back_populates="competence")


class EvaluationCompetence(Base, TimestampMixin):
    __tablename__ = "evaluations_competences"
    __table_args__ = (
        UniqueConstraint("eleve_id", "competence_id", "periode_id", name="uq_eval_comp_eleve_periode"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=False)
    competence_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("competences.id", ondelete="CASCADE"), nullable=False
    )
    periode_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("periodes.id"), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False)
    appreciation: Mapped[str | None] = mapped_column(Text, nullable=True)

    competence: Mapped[Competence] = relationship(back_populates="evaluations")


class DecisionPassage(Base, TimestampMixin):
    __tablename__ = "decisions_passage"
    __table_args__ = (
        UniqueConstraint("eleve_id", "annee_scolaire_id", name="uq_decision_eleve_annee"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)
