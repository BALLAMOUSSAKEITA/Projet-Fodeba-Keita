from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.notes import EleveMoyennesItem


class BulletinEleveData(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    classe_nom: str
    periode_libelle: str
    annee_libelle: str
    moyennes: EleveMoyennesItem
    decision: str | None = None
    observation: str | None = None


class StatsPedagogiquesResponse(BaseModel):
    classe_id: UUID
    classe_nom: str
    periode_libelle: str
    effectif: int
    moyenne_classe: Decimal | None
    taux_reussite: Decimal | None
    meilleur_eleve: str | None
    moins_bonne_moyenne: Decimal | None


class PalmaresItem(BaseModel):
    rang: int
    eleve_id: UUID
    nom: str
    prenoms: str
    matricule: str
    moyenne_generale: Decimal
    appreciation: str | None


class PalmaresResponse(BaseModel):
    classe_id: UUID
    classe_nom: str
    periode_libelle: str
    items: list[PalmaresItem]


class DecisionPassageCreate(BaseModel):
    eleve_id: UUID
    decision: str = Field(..., pattern=r"^(admis|redouble|exclu)$")
    observation: str | None = None
    annee_scolaire_id: UUID | None = None


class DecisionPassageResponse(BaseModel):
    id: UUID
    eleve_id: UUID
    annee_scolaire_id: UUID
    decision: str
    observation: str | None

    model_config = {"from_attributes": True}


class CompetenceResponse(BaseModel):
    id: UUID
    code: str
    domaine: str
    libelle: str
    niveau_id: UUID
    ordre: int

    model_config = {"from_attributes": True}


class CompetenceEvalItem(BaseModel):
    competence_id: UUID
    statut: str = Field(..., pattern=r"^(acquis|en_cours|non_acquis)$")
    appreciation: str | None = None


class CompetenceBulkUpdate(BaseModel):
    eleve_id: UUID
    evaluations: list[CompetenceEvalItem]


class CompetenceGrilleRow(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    evaluations: dict[str, str | None]


class CompetenceGrilleResponse(BaseModel):
    classe_id: UUID
    classe_nom: str
    periode_libelle: str
    competences: list[CompetenceResponse]
    eleves: list[CompetenceGrilleRow]
