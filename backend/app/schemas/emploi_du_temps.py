from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field


JOURS_LABELS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]


class CreneauCreate(BaseModel):
    libelle: str = Field(..., min_length=1, max_length=50)
    heure_debut: time
    heure_fin: time
    ordre: int = Field(..., ge=1, le=20)
    annee_scolaire_id: UUID | None = None


class CreneauUpdate(BaseModel):
    libelle: str | None = Field(default=None, min_length=1, max_length=50)
    heure_debut: time | None = None
    heure_fin: time | None = None
    ordre: int | None = Field(default=None, ge=1, le=20)


class CreneauResponse(BaseModel):
    id: UUID
    libelle: str
    heure_debut: time
    heure_fin: time
    ordre: int
    annee_scolaire_id: UUID

    model_config = {"from_attributes": True}


class SeanceCreate(BaseModel):
    classe_id: UUID
    creneau_id: UUID
    jour_semaine: int = Field(..., ge=0, le=4)
    matiere_id: UUID
    personnel_id: UUID
    salle: str | None = None
    annee_scolaire_id: UUID | None = None


class SeanceUpdate(BaseModel):
    creneau_id: UUID | None = None
    jour_semaine: int | None = Field(default=None, ge=0, le=4)
    matiere_id: UUID | None = None
    personnel_id: UUID | None = None
    salle: str | None = None


class MatiereBrief(BaseModel):
    id: UUID
    code: str
    libelle: str

    model_config = {"from_attributes": True}


class PersonnelBrief(BaseModel):
    id: UUID
    nom: str
    prenoms: str

    model_config = {"from_attributes": True}


class ClasseBrief(BaseModel):
    id: UUID
    nom: str

    model_config = {"from_attributes": True}


class SeanceResponse(BaseModel):
    id: UUID
    classe_id: UUID
    creneau_id: UUID
    jour_semaine: int
    matiere_id: UUID
    personnel_id: UUID
    salle: str | None
    annee_scolaire_id: UUID
    matiere: MatiereBrief | None = None
    personnel: PersonnelBrief | None = None
    classe: ClasseBrief | None = None
    creneau: CreneauResponse | None = None

    model_config = {"from_attributes": True}


class LigneGrille(BaseModel):
    creneau: CreneauResponse
    cellules: list[SeanceResponse | None]


class GrilleEdtResponse(BaseModel):
    titre: str
    jours: list[str]
    lignes: list[LigneGrille]
    conflits: list["ConflitEdt"]


class ConflitEdt(BaseModel):
    type: str
    message: str
    seance_ids: list[UUID]


class ConflitsListResponse(BaseModel):
    items: list[ConflitEdt]
    total: int
