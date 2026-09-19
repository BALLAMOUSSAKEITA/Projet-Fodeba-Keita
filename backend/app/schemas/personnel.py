from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class DiplomeBase(BaseModel):
    libelle: str = Field(..., min_length=2, max_length=200)
    etablissement: str | None = None
    annee_obtention: int | None = Field(default=None, ge=1950, le=2100)
    niveau: str | None = None


class DiplomeCreate(DiplomeBase):
    pass


class DiplomeUpdate(BaseModel):
    libelle: str | None = Field(default=None, min_length=2, max_length=200)
    etablissement: str | None = None
    annee_obtention: int | None = Field(default=None, ge=1950, le=2100)
    niveau: str | None = None


class DiplomeResponse(DiplomeBase):
    id: UUID
    personnel_id: UUID

    model_config = {"from_attributes": True}


class ContratBase(BaseModel):
    type_contrat: str = Field(..., pattern=r"^(cdi|cdd|vacataire)$")
    date_debut: date
    date_fin: date | None = None
    salaire_mensuel: Decimal | None = Field(default=None, ge=0)
    statut: str = Field(default="actif", pattern=r"^(actif|termine)$")


class ContratCreate(ContratBase):
    pass


class ContratUpdate(BaseModel):
    type_contrat: str | None = Field(default=None, pattern=r"^(cdi|cdd|vacataire)$")
    date_debut: date | None = None
    date_fin: date | None = None
    salaire_mensuel: Decimal | None = Field(default=None, ge=0)
    statut: str | None = Field(default=None, pattern=r"^(actif|termine)$")


class ContratResponse(ContratBase):
    id: UUID
    personnel_id: UUID

    model_config = {"from_attributes": True}


class ClasseBrief(BaseModel):
    id: UUID
    nom: str

    model_config = {"from_attributes": True}


class MatiereBrief(BaseModel):
    id: UUID
    code: str
    libelle: str

    model_config = {"from_attributes": True}


class AffectationCreate(BaseModel):
    classe_id: UUID
    matiere_id: UUID
    annee_scolaire_id: UUID | None = None


class AffectationResponse(BaseModel):
    id: UUID
    personnel_id: UUID
    classe_id: UUID
    matiere_id: UUID
    annee_scolaire_id: UUID
    classe: ClasseBrief | None = None
    matiere: MatiereBrief | None = None

    model_config = {"from_attributes": True}


class TitulaireRequest(BaseModel):
    classe_id: UUID


class CongeBase(BaseModel):
    type: str = Field(..., pattern=r"^(conge|maladie|permission|absence)$")
    date_debut: date
    date_fin: date
    motif: str | None = None
    statut: str = Field(default="demande", pattern=r"^(demande|approuve|refuse)$")


class CongeCreate(CongeBase):
    pass


class CongeUpdate(BaseModel):
    type: str | None = Field(default=None, pattern=r"^(conge|maladie|permission|absence)$")
    date_debut: date | None = None
    date_fin: date | None = None
    motif: str | None = None
    statut: str | None = Field(default=None, pattern=r"^(demande|approuve|refuse)$")


class CongeResponse(CongeBase):
    id: UUID
    personnel_id: UUID

    model_config = {"from_attributes": True}


class PersonnelCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    sexe: str = Field(..., pattern=r"^(M|F)$")
    date_naissance: date | None = None
    telephone: str = Field(..., min_length=6, max_length=20)
    email: str | None = None
    adresse: str | None = None
    categorie: str = Field(..., pattern=r"^(enseignant|non_enseignant)$")
    fonction: str | None = None
    specialite: str | None = None
    date_embauche: date | None = None
    user_id: UUID | None = None


class PersonnelUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenoms: str | None = Field(default=None, min_length=1, max_length=150)
    sexe: str | None = Field(default=None, pattern=r"^(M|F)$")
    date_naissance: date | None = None
    telephone: str | None = Field(default=None, min_length=6, max_length=20)
    email: str | None = None
    adresse: str | None = None
    fonction: str | None = None
    specialite: str | None = None
    date_embauche: date | None = None
    statut: str | None = Field(default=None, pattern=r"^(actif|inactif)$")
    user_id: UUID | None = None


class PersonnelListItem(BaseModel):
    id: UUID
    matricule: str
    nom: str
    prenoms: str
    sexe: str
    telephone: str
    email: str | None
    categorie: str
    fonction: str | None
    specialite: str | None
    statut: str

    model_config = {"from_attributes": True}


class PersonnelResponse(BaseModel):
    id: UUID
    matricule: str
    nom: str
    prenoms: str
    sexe: str
    date_naissance: date | None
    telephone: str
    email: str | None
    adresse: str | None
    categorie: str
    fonction: str | None
    specialite: str | None
    date_embauche: date | None
    statut: str
    user_id: UUID | None
    created_at: datetime
    diplomes: list[DiplomeResponse] = []
    contrats: list[ContratResponse] = []
    affectations: list[AffectationResponse] = []
    conges: list[CongeResponse] = []
    classes_titulaire: list[ClasseBrief] = []

    model_config = {"from_attributes": True}


class PersonnelListResponse(BaseModel):
    items: list[PersonnelListItem]
    total: int
