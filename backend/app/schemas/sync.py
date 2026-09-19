from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.eleve import EleveListItem


class SyncNoteChange(BaseModel):
    id: UUID
    evaluation_id: UUID
    eleve_id: UUID
    valeur: Decimal | None
    is_absent: bool
    updated_at: datetime


class SyncPresenceChange(BaseModel):
    id: UUID
    appel_id: UUID
    classe_id: UUID
    appel_date: date
    eleve_id: UUID
    statut: str
    updated_at: datetime


class SyncPaiementChange(BaseModel):
    id: UUID
    eleve_id: UUID
    type_frais_id: UUID
    montant: Decimal
    mode_paiement: str
    numero_recu: str
    statut: str
    updated_at: datetime


class SyncClasseItem(BaseModel):
    id: UUID
    nom: str
    capacite_max: int
    salle: str | None = None
    niveau_code: str | None = None


class SyncPullResponse(BaseModel):
    server_time: datetime
    eleves: list[EleveListItem]
    eleves_total: int
    classes: list[SyncClasseItem]
    notes_changes: list[SyncNoteChange] = Field(default_factory=list)
    presences_changes: list[SyncPresenceChange] = Field(default_factory=list)
    paiements_changes: list[SyncPaiementChange] = Field(default_factory=list)


class SyncPushItem(BaseModel):
    client_id: str = Field(..., min_length=1, max_length=64)
    entity_type: Literal["notes", "presence", "paiement"]
    client_updated_at: datetime
    resolve_strategy: Literal["server_wins", "client_wins"] = "client_wins"
    payload: dict[str, Any]


class SyncConflictDetail(BaseModel):
    entity_type: str
    server_updated_at: datetime
    client_updated_at: datetime
    server_snapshot: dict[str, Any] | None = None


class SyncPushResultItem(BaseModel):
    client_id: str
    status: Literal["applied", "conflict", "error", "duplicate"]
    entity_type: str
    server_id: str | None = None
    message: str | None = None
    conflict: SyncConflictDetail | None = None


class SyncPushRequest(BaseModel):
    operations: list[SyncPushItem] = Field(..., min_length=1, max_length=100)


class SyncPushResponse(BaseModel):
    results: list[SyncPushResultItem]
    applied: int
    conflicts: int
    errors: int
