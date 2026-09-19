export type CategorieDepense = {
  id: string;
  code: string;
  libelle: string;
  actif: boolean;
};

export type CompteTresorerie = {
  id: string;
  code: string;
  libelle: string;
  type: string;
  solde_initial: string;
  solde_actuel?: string;
  actif: boolean;
};

export type Depense = {
  id: string;
  categorie_id: string;
  categorie_libelle: string;
  annee_scolaire_id: string;
  libelle: string;
  montant: string;
  date_depense: string;
  compte_tresorerie_id: string;
  compte_libelle: string;
  statut: string;
  reference_piece: string | null;
  motif_refus: string | null;
};

export type BudgetSuiviItem = {
  categorie_id: string;
  categorie_code: string;
  categorie_libelle: string;
  montant_prevu: string;
  montant_realise: string;
  ecart: string;
  taux_realisation: string | null;
};

export type BudgetSuivi = {
  annee_scolaire_id: string;
  annee_libelle: string;
  total_prevu: string;
  total_realise: string;
  lignes: BudgetSuiviItem[];
};

export type Ecriture = {
  id: string;
  date_ecriture: string;
  type: string;
  libelle: string;
  montant: string;
  compte_libelle: string;
  source_type: string | null;
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

export type Tresorerie = {
  comptes: CompteTresorerie[];
  total_caisse: string;
  total_banque: string;
  total_general: string;
};
