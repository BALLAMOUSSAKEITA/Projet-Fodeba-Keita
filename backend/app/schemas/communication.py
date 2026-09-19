from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnnonceCreate(BaseModel):
    titre: str = Field(..., min_length=3, max_length=200)
    contenu: str = Field(..., min_length=10)
    audience: str = Field(default="tous", pattern=r"^(tous|parents|personnel)$")
    date_expiration: date | None = None
    annee_scolaire_id: UUID | None = None


class AnnonceResponse(BaseModel):
    id: UUID
    titre: str
    contenu: str
    audience: str
    statut: str
    date_publication: date | None
    date_expiration: date | None
    auteur_nom: str | None = None

    model_config = {"from_attributes": True}


class ModeleMessageCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=30)
    libelle: str = Field(..., min_length=3)
    sujet: str = Field(..., min_length=3)
    corps: str = Field(..., min_length=10)
    canal: str = Field(..., pattern=r"^(sms|email|app|interne)$")


class ModeleMessageResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    sujet: str
    corps: str
    canal: str
    actif: bool

    model_config = {"from_attributes": True}


class EnvoiMessageCreate(BaseModel):
    modele_id: UUID | None = None
    canal: str = Field(..., pattern=r"^(sms|email|app|interne)$")
    destinataire: str = Field(..., min_length=3)
    sujet: str = Field(..., min_length=3)
    corps: str = Field(..., min_length=3)
    eleve_id: UUID | None = None


class HistoriqueResponse(BaseModel):
    id: UUID
    canal: str
    destinataire: str
    sujet: str
    corps: str
    statut: str
    envoye_le: datetime | None
    eleve_id: UUID | None

    model_config = {"from_attributes": True}


class EnfantItem(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    classe_nom: str | None


class PeriodeNoteItem(BaseModel):
    periode_id: UUID
    periode_libelle: str
    moyenne_generale: str | None
    rang: int | None


class PortailResumeResponse(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    classe_nom: str | None
    annee_libelle: str
    total_du: str
    total_paye: str
    total_restant: str
    jours_absents: int
    absences_non_justifiees: int
    jours_retards: int
    incidents_count: int
    periodes_notes: list[PeriodeNoteItem]
    annonces: list[AnnonceResponse]
