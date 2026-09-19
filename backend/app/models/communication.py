import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class StatutAnnonce(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIEE = "publiee"
    ARCHIVEE = "archivee"


class AudienceAnnonce(str, enum.Enum):
    TOUS = "tous"
    PARENTS = "parents"
    PERSONNEL = "personnel"


class CanalCommunication(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    APP = "app"
    INTERNE = "interne"


class StatutEnvoi(str, enum.Enum):
    SIMULE = "simule"
    ENVOYE = "envoye"
    ECHEC = "echec"


class Annonce(Base, TimestampMixin):
    __tablename__ = "annonces"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(String(20), default=AudienceAnnonce.TOUS.value, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutAnnonce.BROUILLON.value, nullable=False)
    date_publication: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_expiration: Mapped[date | None] = mapped_column(Date, nullable=True)
    auteur_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    annee_scolaire_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("annees_scolaires.id"), nullable=True
    )


class ModeleMessage(Base, TimestampMixin):
    __tablename__ = "modeles_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    sujet: Mapped[str] = mapped_column(String(200), nullable=False)
    corps: Mapped[str] = mapped_column(Text, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    actif: Mapped[bool] = mapped_column(default=True, nullable=False)


class HistoriqueCommunication(Base, TimestampMixin):
    __tablename__ = "historique_communications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    modele_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("modeles_messages.id"), nullable=True
    )
    annonce_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("annonces.id"), nullable=True)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    destinataire: Mapped[str] = mapped_column(String(255), nullable=False)
    sujet: Mapped[str] = mapped_column(String(200), nullable=False)
    corps: Mapped[str] = mapped_column(Text, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default=StatutEnvoi.SIMULE.value, nullable=False)
    envoye_par_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    eleve_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("eleves.id"), nullable=True)
    envoye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
