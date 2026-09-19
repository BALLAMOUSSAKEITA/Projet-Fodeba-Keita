import enum
import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class StatutPresence(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    RETARD = "retard"
    EXCUSE = "excuse"


class StatutJustification(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    ACCEPTEE = "acceptee"
    REFUSEE = "refusee"


class TypeIncident(str, enum.Enum):
    AVERTISSEMENT = "avertissement"
    BLAME = "blame"
    EXCLUSION_TEMPORAIRE = "exclusion_temporaire"
    CONVOCATION = "convocation"
    AUTRE = "autre"


class AppelPresence(Base, TimestampMixin):
    __tablename__ = "appels_presence"
    __table_args__ = (UniqueConstraint("classe_id", "date", name="uq_appel_classe_date"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    classe_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    saisi_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    remarque: Mapped[str | None] = mapped_column(Text, nullable=True)

    presences: Mapped[list["PresenceEleve"]] = relationship(
        back_populates="appel",
        cascade="all, delete-orphan",
    )


class PresenceEleve(Base, TimestampMixin):
    __tablename__ = "presences_eleves"
    __table_args__ = (UniqueConstraint("appel_id", "eleve_id", name="uq_presence_appel_eleve"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    appel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("appels_presence.id", ondelete="CASCADE"), nullable=False, index=True
    )
    eleve_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default=StatutPresence.PRESENT.value)
    retard_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motif: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification_statut: Mapped[str | None] = mapped_column(String(20), nullable=True)

    appel: Mapped["AppelPresence"] = relationship(back_populates="presences")


class IncidentDisciplinaire(Base, TimestampMixin):
    __tablename__ = "incidents_disciplinaires"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    eleve_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("eleves.id", ondelete="CASCADE"), nullable=False, index=True
    )
    classe_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sanction: Mapped[str | None] = mapped_column(Text, nullable=True)
    saisi_par_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
