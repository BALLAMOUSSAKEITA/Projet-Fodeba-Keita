from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PresenceEleveItem(BaseModel):
    eleve_id: UUID
    statut: str = Field(..., pattern=r"^(present|absent|retard|excuse)$")
    retard_minutes: int | None = Field(default=None, ge=0, le=480)
    motif: str | None = None


class AppelBulkUpdate(BaseModel):
    presences: list[PresenceEleveItem]
    remarque: str | None = None


class PresenceEleveRow(BaseModel):
    presence_id: UUID | None
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    statut: str
    retard_minutes: int | None
    motif: str | None
    justification: str | None
    justification_statut: str | None


class AppelPresenceResponse(BaseModel):
    appel_id: UUID | None
    classe_id: UUID
    classe_nom: str
    date: date
    remarque: str | None
    eleves: list[PresenceEleveRow]


class JustificationUpdate(BaseModel):
    justification: str = Field(..., min_length=3)
    accepter: bool = False


class JustificationReview(BaseModel):
    statut: str = Field(..., pattern=r"^(acceptee|refusee)$")
    commentaire: str | None = None


class EleveRecapItem(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    jours_absents: int
    jours_retards: int
    minutes_retard_total: int
    jours_excuses: int
    absences_non_justifiees: int


class ClasseRecapResponse(BaseModel):
    classe_id: UUID
    classe_nom: str
    date_debut: date
    date_fin: date
    effectif: int
    eleves: list[EleveRecapItem]


class EleveRecapResponse(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    date_debut: date
    date_fin: date
    jours_absents: int
    jours_retards: int
    minutes_retard_total: int
    jours_excuses: int
    absences_non_justifiees: int
    incidents_count: int


class EnseignantAbsenceItem(BaseModel):
    personnel_id: UUID
    matricule: str
    nom: str
    prenoms: str
    type_conge: str
    date_debut: date
    date_fin: date
    statut: str


class IncidentCreate(BaseModel):
    eleve_id: UUID
    classe_id: UUID | None = None
    date: date
    type: str = Field(..., pattern=r"^(avertissement|blame|exclusion_temporaire|convocation|autre)$")
    description: str = Field(..., min_length=5)
    sanction: str | None = None


class IncidentUpdate(BaseModel):
    type: str | None = Field(default=None, pattern=r"^(avertissement|blame|exclusion_temporaire|convocation|autre)$")
    description: str | None = Field(default=None, min_length=5)
    sanction: str | None = None


class IncidentResponse(BaseModel):
    id: UUID
    eleve_id: UUID
    eleve_nom: str
    eleve_prenoms: str
    classe_id: UUID | None
    classe_nom: str | None
    date: date
    type: str
    description: str
    sanction: str | None

    model_config = {"from_attributes": True}
