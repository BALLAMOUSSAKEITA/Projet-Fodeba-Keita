from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TarifNiveauCreate(BaseModel):
    annee_scolaire_id: UUID
    niveau_id: UUID
    type_frais_id: UUID
    montant: Decimal = Field(..., ge=0)


class TarifNiveauResponse(BaseModel):
    id: UUID
    annee_scolaire_id: UUID
    niveau_id: UUID
    niveau_code: str | None = None
    niveau_libelle: str | None = None
    type_frais_id: UUID
    type_frais_code: str | None = None
    type_frais_libelle: str | None = None
    montant: Decimal

    model_config = {"from_attributes": True}


class TrancheFraisCreate(BaseModel):
    annee_scolaire_id: UUID
    type_frais_id: UUID
    libelle: str
    date_echeance: date
    ordre: int = Field(..., ge=1)
    pourcentage: Decimal = Field(..., ge=0, le=100)


class TrancheFraisResponse(BaseModel):
    id: UUID
    annee_scolaire_id: UUID
    type_frais_id: UUID
    type_frais_libelle: str | None = None
    libelle: str
    date_echeance: date
    ordre: int
    pourcentage: Decimal

    model_config = {"from_attributes": True}


class RemiseEleveCreate(BaseModel):
    eleve_id: UUID
    annee_scolaire_id: UUID
    type_frais_id: UUID | None = None
    montant: Decimal = Field(default=Decimal("0"), ge=0)
    pourcentage: Decimal | None = Field(default=None, ge=0, le=100)
    motif: str = Field(..., min_length=3)


class RemiseEleveResponse(BaseModel):
    id: UUID
    eleve_id: UUID
    annee_scolaire_id: UUID
    type_frais_id: UUID | None
    montant: Decimal
    pourcentage: Decimal | None
    motif: str

    model_config = {"from_attributes": True}


class PaiementCreate(BaseModel):
    eleve_id: UUID
    annee_scolaire_id: UUID | None = None
    type_frais_id: UUID
    tranche_id: UUID | None = None
    montant: Decimal = Field(..., gt=0)
    remise_montant: Decimal = Field(default=Decimal("0"), ge=0)
    mode_paiement: str = Field(
        ...,
        pattern=r"^(especes|orange_money|mtn_momo|virement|cheque)$",
    )
    reference_externe: str | None = None
    date_paiement: date | None = None
    libelle: str | None = None


class PaiementAnnulation(BaseModel):
    motif: str = Field(..., min_length=3)


class PaiementRemboursement(BaseModel):
    motif: str = Field(..., min_length=3)
    mode_paiement: str = Field(
        default="especes",
        pattern=r"^(especes|orange_money|mtn_momo|virement|cheque)$",
    )


class PaiementResponse(BaseModel):
    id: UUID
    eleve_id: UUID
    eleve_nom: str
    eleve_prenoms: str
    eleve_matricule: str
    annee_scolaire_id: UUID
    type_frais_id: UUID
    type_frais_libelle: str
    tranche_id: UUID | None
    tranche_libelle: str | None
    montant: Decimal
    remise_montant: Decimal
    mode_paiement: str
    reference_externe: str | None
    date_paiement: date
    numero_recu: str
    statut: str
    libelle: str | None


class LigneSituation(BaseModel):
    type_frais_id: UUID
    type_frais_code: str
    type_frais_libelle: str
    montant_du: Decimal
    montant_paye: Decimal
    montant_restant: Decimal
    remise: Decimal


class TrancheSituation(BaseModel):
    tranche_id: UUID
    libelle: str
    date_echeance: date
    montant_du: Decimal
    montant_paye: Decimal
    en_retard: bool


class SituationEleveResponse(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    annee_scolaire_id: UUID
    annee_libelle: str
    total_du: Decimal
    total_paye: Decimal
    total_restant: Decimal
    lignes: list[LigneSituation]
    tranches: list[TrancheSituation]


class ImpayeItem(BaseModel):
    eleve_id: UUID
    matricule: str
    nom: str
    prenoms: str
    classe_nom: str | None
    montant_du: Decimal
    montant_paye: Decimal
    montant_restant: Decimal
    tranches_en_retard: int
    derniere_relance: date | None


class RelanceCreate(BaseModel):
    eleve_id: UUID
    annee_scolaire_id: UUID | None = None
    tranche_id: UUID | None = None
    canal: str = Field(..., pattern=r"^(sms|appel|courrier|email)$")
    message: str | None = None


class RelanceResponse(BaseModel):
    id: UUID
    eleve_id: UUID
    date_relance: date
    canal: str
    message: str | None

    model_config = {"from_attributes": True}


class CaisseJournaliereResponse(BaseModel):
    date: date
    total_encaisse: Decimal
    nombre_paiements: int
    par_mode: dict[str, Decimal]
    paiements: list[PaiementResponse]
