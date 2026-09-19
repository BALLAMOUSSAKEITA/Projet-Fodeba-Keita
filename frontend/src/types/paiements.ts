export interface Paiement {
  id: string;
  eleve_id: string;
  eleve_nom: string;
  eleve_prenoms: string;
  eleve_matricule: string;
  type_frais_id: string;
  type_frais_libelle: string;
  tranche_id: string | null;
  tranche_libelle: string | null;
  montant: number;
  remise_montant: number;
  mode_paiement: string;
  reference_externe: string | null;
  date_paiement: string;
  numero_recu: string;
  statut: string;
  libelle: string | null;
}

export interface SituationEleve {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  annee_libelle: string;
  total_du: number;
  total_paye: number;
  total_restant: number;
  lignes: {
    type_frais_libelle: string;
    montant_du: number;
    montant_paye: number;
    montant_restant: number;
  }[];
}

export interface ImpayeItem {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  classe_nom: string | null;
  montant_du: number;
  montant_paye: number;
  montant_restant: number;
  tranches_en_retard: number;
  derniere_relance: string | null;
}

export interface CaisseJournaliere {
  date: string;
  total_encaisse: number;
  nombre_paiements: number;
  par_mode: Record<string, number>;
  paiements: Paiement[];
}

export interface TypeFraisOption {
  id: string;
  code: string;
  libelle: string;
}

export interface TrancheOption {
  id: string;
  libelle: string;
  type_frais_id: string;
}
