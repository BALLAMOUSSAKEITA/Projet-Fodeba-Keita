import enum
import uuid
from datetime import time

from sqlalchemy import ForeignKey, Integer, String, Time, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class JourSemaine(int, enum.Enum):
    LUNDI = 0
    MARDI = 1
    MERCREDI = 2
    JEUDI = 3
    VENDREDI = 4


class CreneauHoraire(Base, TimestampMixin):
    __tablename__ = "creneaux_horaires"
    __table_args__ = (
        UniqueConstraint("annee_scolaire_id", "ordre", name="uq_creneau_annee_ordre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)
    heure_debut: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin: Mapped[time] = mapped_column(Time, nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    seances: Mapped[list["SeanceCours"]] = relationship(back_populates="creneau")


class SeanceCours(Base, TimestampMixin):
    __tablename__ = "seances_cours"
    __table_args__ = (
        UniqueConstraint(
            "classe_id",
            "creneau_id",
            "jour_semaine",
            "annee_scolaire_id",
            name="uq_seance_classe_creneau_jour",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    classe_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("classes.id"), nullable=False)
    creneau_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("creneaux_horaires.id"), nullable=False
    )
    jour_semaine: Mapped[int] = mapped_column(Integer, nullable=False)
    matiere_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("matieres.id"), nullable=False)
    personnel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("personnel.id"), nullable=False)
    salle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    annee_scolaire_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=False
    )

    creneau: Mapped[CreneauHoraire] = relationship(back_populates="seances")
    classe: Mapped["Classe"] = relationship("Classe")
    matiere: Mapped["Matiere"] = relationship("Matiere")
    personnel: Mapped["Personnel"] = relationship("Personnel")
