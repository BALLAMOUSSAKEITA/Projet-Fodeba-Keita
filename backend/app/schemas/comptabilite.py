from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CategorieDepenseResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    actif: bool

    model_config = {"from_attributes": True}


class CompteTresorerieResponse(BaseModel):
    id: UUID
    code: str
    libelle: str
    type: str
    solde_initial: Decimal
    solde_actuel: Decimal | None = None
    actif: bool

    model_config = {"from_attributes": True}


class DepenseCreate(BaseModel):
    categorie_id: UUID
    annee_scolaire_id: UUID | None = None
    libelle: str = Field(..., min_length=3)
    montant: Decimal = Field(..., gt=0)
    date_depense: date
    compte_tresorerie_id: UUID
    reference_piece: str | None = None


class DepenseRefus(BaseModel):
    motif: str = Field(..., min_length=3)


class DepenseResponse(BaseModel):
    id: UUID
    categorie_id: UUID
    categorie_libelle: str
    annee_scolaire_id: UUID
    libelle: str
    montant: Decimal
    date_depense: date
    compte_tresorerie_id: UUID
    compte_libelle: str
    statut: str
    reference_piece: str | None
    motif_refus: str | None


class BudgetLigneCreate(BaseModel):
    annee_scolaire_id: UUID
    categorie_id: UUID
    montant_prevu: Decimal = Field(..., ge=0)


class BudgetSuiviItem(BaseModel):
    categorie_id: UUID
    categorie_code: str
    categorie_libelle: str
    montant_prevu: Decimal
    montant_realise: Decimal
    ecart: Decimal
    taux_realisation: Decimal | None


class BudgetSuiviResponse(BaseModel):
    annee_scolaire_id: UUID
    annee_libelle: str
    total_prevu: Decimal
    total_realise: Decimal
    lignes: list[BudgetSuiviItem]


class EcritureResponse(BaseModel):
    id: UUID
    date_ecriture: date
    type: str
    libelle: str
    montant: Decimal
    compte_libelle: str
    source_type: str | None


class RapportFinancierResponse(BaseModel):
    periode_debut: date
    periode_fin: date
    total_recettes: Decimal
    total_depenses: Decimal
    solde: Decimal
    recettes_par_mode: dict[str, Decimal]
    depenses_par_categorie: dict[str, Decimal]


class TresorerieResponse(BaseModel):
    comptes: list[CompteTresorerieResponse]
    total_caisse: Decimal
    total_banque: Decimal
    total_general: Decimal
