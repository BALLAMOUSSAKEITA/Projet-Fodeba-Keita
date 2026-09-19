from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TypeEvaluationCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=20)
    libelle: str = Field(..., min_length=2, max_length=100)
    coefficient_defaut: Decimal = Field(default=Decimal("1"), ge=0)
    annee_scolaire_id: UUID | None = None


class TypeEvaluationResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    coefficient_defaut: Decimal
    annee_scolaire_id: UUID

    model_config = {"from_attributes": True}


class EvaluationCreate(BaseModel):
    libelle: str = Field(..., min_length=1, max_length=100)
    classe_id: UUID
    matiere_id: UUID
    periode_id: UUID
    type_evaluation_id: UUID
    coefficient: Decimal | None = None
    date_evaluation: date | None = None


class EvaluationResponse(BaseModel):
    id: UUID
    libelle: str
    classe_id: UUID
    matiere_id: UUID
    periode_id: UUID
    type_evaluation_id: UUID
    coefficient: Decimal
    date_evaluation: date | None
    annee_scolaire_id: UUID
    type_evaluation: TypeEvaluationResponse | None = None

    model_config = {"from_attributes": True}


class NoteItem(BaseModel):
    eleve_id: UUID
    valeur: Decimal | None = None
    is_absent: bool = False
    appreciation_libre: str | None = None


class NotesBulkUpdate(BaseModel):
    notes: list[NoteItem]


class NoteResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    eleve_id: UUID
    valeur: Decimal | None
    is_absent: bool
    appreciation_libre: str | None
    appreciation_auto: str | None

    model_config = {"from_attributes": True}


class EleveNoteRow(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    note: NoteResponse | None = None


class GrilleNotesResponse(BaseModel):
    evaluation: EvaluationResponse
    verrouille: bool
    eleves: list[EleveNoteRow]
    bareme_max: Decimal
    echelle: str


class MoyenneMatiereItem(BaseModel):
    matiere_id: UUID
    matiere_code: str
    matiere_libelle: str
    coefficient_matiere: Decimal
    moyenne: Decimal | None
    appreciation_auto: str | None


class EleveMoyennesItem(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    moyennes_matieres: list[MoyenneMatiereItem]
    moyenne_generale: Decimal | None
    appreciation_generale: str | None
    rang: int | None


class MoyennesClasseResponse(BaseModel):
    classe_id: UUID
    classe_nom: str
    periode_id: UUID
    periode_libelle: str
    verrouille: bool
    eleves: list[EleveMoyennesItem]


class ValidationResponse(BaseModel):
    classe_id: UUID
    periode_id: UUID
    verrouille: bool
    date_validation: date | None
    valide_par_id: UUID | None

    model_config = {"from_attributes": True}
