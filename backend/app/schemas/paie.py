from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PeriodePaieCreate(BaseModel):
    annee: int = Field(..., ge=2020, le=2100)
    mois: int = Field(..., ge=1, le=12)


class PeriodePaieResponse(BaseModel):
    id: UUID
    annee: int
    mois: int
    libelle: str
    statut: str

    model_config = {"from_attributes": True}


class BulletinPaieResponse(BaseModel):
    id: UUID
    personnel_id: UUID
    personnel_matricule: str
    personnel_nom: str
    personnel_prenoms: str
    periode_paie_id: UUID
    periode_libelle: str
    salaire_base: Decimal
    prime_anciennete: Decimal
    prime_autre: Decimal
    indemnite_transport: Decimal
    indemnite_logement: Decimal
    retenue_cnss: Decimal
    retenue_its: Decimal
    retenue_absences: Decimal
    retenue_avances: Decimal
    autres_retenues: Decimal
    brut: Decimal
    net_a_payer: Decimal
    jours_absence: int
    statut: str


class BulletinPaieUpdate(BaseModel):
    prime_autre: Decimal | None = Field(default=None, ge=0)
    indemnite_logement: Decimal | None = Field(default=None, ge=0)
    autres_retenues: Decimal | None = Field(default=None, ge=0)


class AvanceSalaireCreate(BaseModel):
    personnel_id: UUID
    montant: Decimal = Field(..., gt=0)
    date_avance: str
    motif: str | None = None


class AvanceSalaireResponse(BaseModel):
    id: UUID
    personnel_id: UUID
    personnel_nom: str
    personnel_prenoms: str
    montant: Decimal
    date_avance: date
    motif: str | None
    statut: str

    model_config = {"from_attributes": True}


class MasseSalarialeResponse(BaseModel):
    periode_paie_id: UUID
    periode_libelle: str
    nombre_bulletins: int
    total_brut: Decimal
    total_net: Decimal
    total_cnss: Decimal
    total_its: Decimal
    total_paye: Decimal
    total_a_payer: Decimal
    bulletins: list[BulletinPaieResponse]
