from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    user_email: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoriqueNoteResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    eleve_id: UUID
    annee_scolaire_id: UUID
    ancienne_valeur: str | None
    nouvelle_valeur: str | None
    ancien_absent: bool | None
    nouveau_absent: bool | None
    modifie_par_id: UUID | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoriquePaiementResponse(BaseModel):
    id: UUID
    paiement_id: UUID
    eleve_id: UUID
    annee_scolaire_id: UUID
    action: str
    montant: str
    statut_avant: str | None
    statut_apres: str
    details: str | None
    modifie_par_id: UUID | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SauvegardeStatusResponse(BaseModel):
    repertoire: str
    derniere_sauvegarde: str | None
    taille_octets: int | None
    chiffrement: str
    procedure_restauration: str
    https_requis: bool
