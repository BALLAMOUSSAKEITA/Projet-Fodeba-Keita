from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class EtablissementBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    adresse: str | None = None
    region: str | None = None
    prefecture: str | None = None
    commune: str | None = None
    telephone: str | None = None
    email: EmailStr | None = None
    logo_url: str | None = None
    devise_principale: str = "GNF"
    devise_secondaire: str | None = None


class EtablissementUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=2, max_length=255)
    code: str | None = Field(default=None, min_length=2, max_length=50)
    adresse: str | None = None
    region: str | None = None
    prefecture: str | None = None
    commune: str | None = None
    telephone: str | None = None
    email: EmailStr | None = None
    logo_url: str | None = None
    devise_principale: str | None = None
    devise_secondaire: str | None = None


class EtablissementResponse(EtablissementBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnneeScolaireCreate(BaseModel):
    libelle: str = Field(..., examples=["2025-2026"])
    date_debut: date
    date_fin: date


class AnneeScolaireUpdate(BaseModel):
    libelle: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    statut: str | None = None


class AnneeScolaireResponse(BaseModel):
    id: UUID
    libelle: str
    date_debut: date
    date_fin: date
    statut: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NiveauCreate(BaseModel):
    code: str
    libelle: str
    ordre: int
    type: str


class NiveauUpdate(BaseModel):
    libelle: str | None = None
    ordre: int | None = None
    type: str | None = None


class NiveauResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    ordre: int
    type: str

    model_config = {"from_attributes": True}


class ClasseCreate(BaseModel):
    nom: str
    capacite_max: int = Field(default=40, ge=1, le=200)
    salle: str | None = None
    niveau_id: UUID
    annee_scolaire_id: UUID


class ClasseUpdate(BaseModel):
    nom: str | None = None
    capacite_max: int | None = Field(default=None, ge=1, le=200)
    salle: str | None = None
    niveau_id: UUID | None = None


class ClasseResponse(BaseModel):
    id: UUID
    nom: str
    capacite_max: int
    salle: str | None
    niveau_id: UUID
    annee_scolaire_id: UUID
    niveau: NiveauResponse | None = None

    model_config = {"from_attributes": True}


class MatiereNiveauInput(BaseModel):
    niveau_id: UUID
    coefficient: Decimal = Field(default=Decimal("1"), ge=0)


class MatiereCreate(BaseModel):
    code: str
    libelle: str
    coefficient_defaut: Decimal = Field(default=Decimal("1"), ge=0)
    niveaux: list[MatiereNiveauInput] = []


class MatiereUpdate(BaseModel):
    libelle: str | None = None
    coefficient_defaut: Decimal | None = Field(default=None, ge=0)
    niveaux: list[MatiereNiveauInput] | None = None


class MatiereResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    coefficient_defaut: Decimal
    niveaux: list[NiveauResponse] = []

    model_config = {"from_attributes": True}


class PeriodeCreate(BaseModel):
    libelle: str
    type: str = "trimestre"
    date_debut: date
    date_fin: date
    ordre: int = Field(..., ge=1, le=4)
    annee_scolaire_id: UUID


class PeriodeUpdate(BaseModel):
    libelle: str | None = None
    type: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    ordre: int | None = Field(default=None, ge=1, le=4)


class PeriodeResponse(BaseModel):
    id: UUID
    libelle: str
    type: str
    date_debut: date
    date_fin: date
    ordre: int
    annee_scolaire_id: UUID

    model_config = {"from_attributes": True}


class BaremeUpdate(BaseModel):
    echelle: str = Field(..., pattern=r"^/(10|20|100)$")
    arrondi_decimales: int = Field(default=2, ge=0, le=2)
    seuil_passage: Decimal = Field(default=Decimal("10"), ge=0)
    seuil_redoublement: Decimal = Field(default=Decimal("8"), ge=0)


class BaremeResponse(BaseModel):
    id: UUID
    annee_scolaire_id: UUID
    echelle: str
    arrondi_decimales: int
    seuil_passage: Decimal
    seuil_redoublement: Decimal

    model_config = {"from_attributes": True}


class TypeFraisCreate(BaseModel):
    code: str
    libelle: str
    description: str | None = None
    actif: bool = True


class TypeFraisUpdate(BaseModel):
    libelle: str | None = None
    description: str | None = None
    actif: bool | None = None


class TypeFraisResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    description: str | None
    actif: bool

    model_config = {"from_attributes": True}


class CalendrierCreate(BaseModel):
    libelle: str
    date_debut: date
    date_fin: date
    type: str
    annee_scolaire_id: UUID


class CalendrierUpdate(BaseModel):
    libelle: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    type: str | None = None


class CalendrierResponse(BaseModel):
    id: UUID
    libelle: str
    date_debut: date
    date_fin: date
    type: str
    annee_scolaire_id: UUID

    model_config = {"from_attributes": True}


class ReferentielResponse(BaseModel):
    id: UUID
    type: str
    code: str
    libelle: str
    parent_id: UUID | None

    model_config = {"from_attributes": True}


class ParametrageStatutResponse(BaseModel):
    etablissement_configure: bool
    annee_active: bool
    niveaux_count: int
    classes_count: int
    matieres_count: int
    periodes_count: int
    types_frais_count: int
    pret_pour_inscriptions: bool
