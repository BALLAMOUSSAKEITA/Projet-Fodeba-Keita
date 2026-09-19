export interface ParametrageStatut {
  etablissement_configure: boolean;
  annee_active: boolean;
  niveaux_count: number;
  classes_count: number;
  matieres_count: number;
  periodes_count: number;
  types_frais_count: number;
  pret_pour_inscriptions: boolean;
}

export interface Etablissement {
  id: string;
  nom: string;
  code: string;
  adresse: string | null;
  region: string | null;
  prefecture: string | null;
  commune: string | null;
  telephone: string | null;
  email: string | null;
  logo_url: string | null;
  devise_principale: string;
  devise_secondaire: string | null;
}

export interface AnneeScolaire {
  id: string;
  libelle: string;
  date_debut: string;
  date_fin: string;
  statut: string;
  is_active: boolean;
}

export interface Niveau {
  id: string;
  code: string;
  libelle: string;
  ordre: number;
  type: string;
}

export interface Classe {
  id: string;
  nom: string;
  capacite_max: number;
  salle: string | null;
  niveau_id: string;
  annee_scolaire_id: string;
  niveau?: Niveau;
}

export interface Matiere {
  id: string;
  code: string;
  libelle: string;
  coefficient_defaut: number;
  niveaux: Niveau[];
}

export interface Periode {
  id: string;
  libelle: string;
  type: string;
  date_debut: string;
  date_fin: string;
  ordre: number;
  annee_scolaire_id: string;
}

export interface Bareme {
  id: string;
  annee_scolaire_id: string;
  echelle: string;
  arrondi_decimales: number;
  seuil_passage: number;
  seuil_redoublement: number;
}

export interface TypeFrais {
  id: string;
  code: string;
  libelle: string;
  description: string | null;
  actif: boolean;
}

export interface CalendrierEntry {
  id: string;
  libelle: string;
  date_debut: string;
  date_fin: string;
  type: string;
  annee_scolaire_id: string;
}

export interface Referentiel {
  id: string;
  type: string;
  code: string;
  libelle: string;
}
