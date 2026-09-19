export type DashboardKPI = {
  annee_libelle: string;
  total_eleves: number;
  total_classes: number;
  total_personnel: number;
  recettes_mois: string;
  total_impayes: string;
  taux_presence_mois: number | null;
  nombre_impayes: number;
};

export type SerieGraphique = {
  labels: string[];
  values: number[];
};

export type Graphiques = {
  effectifs_par_niveau: SerieGraphique;
  recettes_par_mois: SerieGraphique;
  repartition_sexe: SerieGraphique;
  depenses_par_categorie: SerieGraphique;
};

export type RapportEffectifs = {
  annee_libelle: string;
  stats: {
    total_eleves: number;
    total_garcons: number;
    total_filles: number;
    par_niveau: { niveau_code: string; niveau_libelle: string; total: number; garcons: number; filles: number }[];
    sans_classe: number;
  };
  par_classe: {
    id: string;
    nom: string;
    niveau_libelle: string;
    effectif: number;
    capacite_max: number;
    places_restantes: number;
  }[];
};

export type RapportPedagogique = {
  periode_id: string;
  periode_libelle: string;
  classes: {
    classe_id: string;
    classe_nom: string;
    effectif: number;
    moyenne_classe: string | null;
    taux_reussite: string | null;
    meilleur_eleve: string | null;
  }[];
};

export type RapportPresence = {
  date_debut: string;
  date_fin: string;
  total_jours_suivis: number;
  jours_absents_total: number;
  jours_retards_total: number;
  taux_presence_global: number | null;
  par_classe: {
    classe_id: string;
    classe_nom: string;
    effectif: number;
    jours_absents: number;
    jours_retards: number;
    taux_presence: number | null;
  }[];
};

export type StatistiquesAnnuelles = {
  etablissement: string;
  annee_libelle: string;
  total_eleves: number;
  total_garcons: number;
  total_filles: number;
  total_classes: number;
  total_recettes: string;
  total_depenses: string;
  solde_financier: string;
  moyenne_generale_etablissement: string | null;
  taux_reussite_global: string | null;
  taux_presence_annuel: number | null;
  nombre_impayes: number;
};

export type RapportFinancier = {
  periode_debut: string;
  periode_fin: string;
  total_recettes: string;
  total_depenses: string;
  solde: string;
  recettes_par_mode: Record<string, string>;
  depenses_par_categorie: Record<string, string>;
};
