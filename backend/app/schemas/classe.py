from uuid import UUID

from pydantic import BaseModel


class ClasseBrief(BaseModel):
    id: UUID
    nom: str
    capacite_max: int
    salle: str | None = None

    model_config = {"from_attributes": True}


class ClasseEffectifResponse(BaseModel):
    id: UUID
    nom: str
    niveau_code: str
    niveau_libelle: str
    capacite_max: int
    effectif: int
    places_restantes: int
    depassement: bool
    salle: str | None = None


class EleveClasseItem(BaseModel):
    id: UUID
    matricule: str
    nom: str
    prenoms: str
    sexe: str
    date_naissance: str

    model_config = {"from_attributes": True}


class ClasseElevesResponse(BaseModel):
    classe: ClasseBrief
    effectif: int
    capacite_max: int
    eleves: list[EleveClasseItem]
