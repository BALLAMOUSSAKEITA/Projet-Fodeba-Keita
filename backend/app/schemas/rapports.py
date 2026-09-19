from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.comptabilite import RapportFinancierResponse
from app.schemas.eleve import EffectifStatsResponse


class SerieGraphique(BaseModel):
    labels: list[str]
    values: list[float]


class DashboardKPIResponse(BaseModel):
    annee_libelle: str
    total_eleves: int
    total_classes: int
    total_personnel: int
    recettes_mois: Decimal
    total_impayes: Decimal
    taux_presence_mois: float | None
    nombre_impayes: int


class RapportEffectifsResponse(BaseModel):
    annee_libelle: str
    stats: EffectifStatsResponse
    par_classe: list[dict]


class RapportPedagogiqueClasseItem(BaseModel):
    classe_id: UUID
    classe_nom: str
    effectif: int
    moyenne_classe: Decimal | None
    taux_reussite: Decimal | None
    meilleur_eleve: str | None


class RapportPedagogiqueResponse(BaseModel):
    periode_id: UUID
    periode_libelle: str
    classes: list[RapportPedagogiqueClasseItem]


class RapportPresenceClasseItem(BaseModel):
    classe_id: UUID
    classe_nom: str
    effectif: int
    jours_absents: int
    jours_retards: int
    taux_presence: float | None


class RapportPresenceResponse(BaseModel):
    date_debut: date
    date_fin: date
    total_jours_suivis: int
    jours_absents_total: int
    jours_retards_total: int
    taux_presence_global: float | None
    par_classe: list[RapportPresenceClasseItem]


class StatistiquesAnnuellesResponse(BaseModel):
    etablissement: str
    annee_libelle: str
    total_eleves: int
    total_garcons: int
    total_filles: int
    total_classes: int
    total_recettes: Decimal
    total_depenses: Decimal
    solde_financier: Decimal
    moyenne_generale_etablissement: Decimal | None
    taux_reussite_global: Decimal | None
    taux_presence_annuel: float | None
    nombre_impayes: int


class GraphiquesResponse(BaseModel):
    effectifs_par_niveau: SerieGraphique
    recettes_par_mois: SerieGraphique
    repartition_sexe: SerieGraphique
    depenses_par_categorie: SerieGraphique


class RapportFinancierWrapper(BaseModel):
    rapport: RapportFinancierResponse
