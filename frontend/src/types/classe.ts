export interface ClasseEffectif {
  id: string;
  nom: string;
  niveau_code: string;
  niveau_libelle: string;
  capacite_max: number;
  effectif: number;
  places_restantes: number;
  depassement: boolean;
  salle: string | null;
}

export interface EleveClasseItem {
  id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance: string;
}

export interface ClasseElevesResponse {
  classe: {
    id: string;
    nom: string;
    capacite_max: number;
    salle: string | null;
  };
  effectif: number;
  capacite_max: number;
  eleves: EleveClasseItem[];
}

export interface EffectifStats {
  total_eleves: number;
  total_garcons: number;
  total_filles: number;
  par_niveau: {
    niveau_code: string;
    niveau_libelle: string;
    total: number;
    garcons: number;
    filles: number;
  }[];
  sans_classe: number;
}

export interface HistoriqueScolaire {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  inscriptions: {
    id: string;
    annee_scolaire_id: string;
    niveau_id: string;
    classe_id: string | null;
    type: string;
    date_inscription: string;
    statut: string;
    niveau?: { id: string; code: string; libelle: string };
    classe?: { id: string; nom: string };
    annee_scolaire?: { id: string; libelle: string };
  }[];
  transferts: {
    id: string;
    type: string;
    ecole: string;
    date_transfert: string;
    motif: string | null;
    observations: string | null;
  }[];
}
