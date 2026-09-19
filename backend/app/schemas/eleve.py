from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TuteurBase(BaseModel):
    type: str = Field(..., pattern=r"^(pere|mere|tuteur)$")
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    telephone: str = Field(..., min_length=6, max_length=20)
    profession: str | None = None
    adresse: str | None = None
    email: str | None = None


class TuteurCreate(TuteurBase):
    pass


class TuteurUpdate(BaseModel):
    type: str | None = Field(default=None, pattern=r"^(pere|mere|tuteur)$")
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenoms: str | None = Field(default=None, min_length=1, max_length=150)
    telephone: str | None = Field(default=None, min_length=6, max_length=20)
    profession: str | None = None
    adresse: str | None = None
    email: str | None = None


class TuteurResponse(TuteurBase):
    id: UUID
    eleve_id: UUID

    model_config = {"from_attributes": True}


class NiveauBrief(BaseModel):
    id: UUID
    code: str
    libelle: str

    model_config = {"from_attributes": True}


class ClasseBrief(BaseModel):
    id: UUID
    nom: str

    model_config = {"from_attributes": True}


class AnneeBrief(BaseModel):
    id: UUID
    libelle: str

    model_config = {"from_attributes": True}


class InscriptionBrief(BaseModel):
    id: UUID
    annee_scolaire_id: UUID
    niveau_id: UUID
    classe_id: UUID | None
    type: str
    date_inscription: date
    statut: str
    niveau: NiveauBrief | None = None
    classe: ClasseBrief | None = None
    annee_scolaire: AnneeBrief | None = None

    model_config = {"from_attributes": True}


class EleveCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    sexe: str = Field(..., pattern=r"^(M|F)$")
    date_naissance: date
    lieu_naissance: str | None = None
    nationalite: str | None = "Guinéenne"
    adresse: str | None = None
    photo_url: str | None = None
    groupe_sanguin: str | None = None
    allergies: str | None = None
    niveau_id: UUID
    tuteurs: list[TuteurCreate] = Field(..., min_length=1)


class EleveUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenoms: str | None = Field(default=None, min_length=1, max_length=150)
    sexe: str | None = Field(default=None, pattern=r"^(M|F)$")
    date_naissance: date | None = None
    lieu_naissance: str | None = None
    nationalite: str | None = None
    adresse: str | None = None
    photo_url: str | None = None
    groupe_sanguin: str | None = None
    allergies: str | None = None


class ReinscriptionRequest(BaseModel):
    niveau_id: UUID
    annee_scolaire_id: UUID | None = None


class EleveListItem(BaseModel):
    id: UUID
    matricule: str
    nom: str
    prenoms: str
    sexe: str
    date_naissance: date
    statut: str
    niveau_libelle: str | None = None
    niveau_code: str | None = None
    classe_nom: str | None = None

    model_config = {"from_attributes": True}


class EleveResponse(BaseModel):
    id: UUID
    matricule: str
    nom: str
    prenoms: str
    sexe: str
    date_naissance: date
    lieu_naissance: str | None
    nationalite: str | None
    adresse: str | None
    photo_url: str | None
    groupe_sanguin: str | None
    allergies: str | None
    statut: str
    created_at: datetime
    tuteurs: list[TuteurResponse] = []
    inscriptions: list[InscriptionBrief] = []

    model_config = {"from_attributes": True}


class EleveListResponse(BaseModel):
    items: list[EleveListItem]
    total: int


class AffecterClasseRequest(BaseModel):
    classe_id: UUID


class TransfertEntrantCreate(EleveCreate):
    ecole_origine: str = Field(..., min_length=2, max_length=255)
    date_transfert: date | None = None
    observations: str | None = None


class TransfertSortantRequest(BaseModel):
    ecole_destination: str = Field(..., min_length=2, max_length=255)
    motif: str | None = None
    date_transfert: date | None = None


class DesactiverEleveRequest(BaseModel):
    motif: str = Field(..., min_length=3, max_length=255)
    date_inactivite: date | None = None


class TransfertResponse(BaseModel):
    id: UUID
    type: str
    ecole: str
    date_transfert: date
    motif: str | None
    observations: str | None

    model_config = {"from_attributes": True}


class HistoriqueScolaireResponse(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    inscriptions: list[InscriptionBrief]
    transferts: list[TransfertResponse]


class EffectifNiveauStat(BaseModel):
    niveau_code: str
    niveau_libelle: str
    total: int
    garcons: int
    filles: int


class EffectifStatsResponse(BaseModel):
    total_eleves: int
    total_garcons: int
    total_filles: int
    par_niveau: list[EffectifNiveauStat]
    sans_classe: int
