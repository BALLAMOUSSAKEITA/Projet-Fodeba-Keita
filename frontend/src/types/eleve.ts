export interface Tuteur {
  id: string;
  eleve_id: string;
  type: string;
  nom: string;
  prenoms: string;
  telephone: string;
  profession: string | null;
  adresse: string | null;
  email: string | null;
}

export interface Inscription {
  id: string;
  annee_scolaire_id: string;
  niveau_id: string;
  classe_id: string | null;
  type: string;
  date_inscription: string;
  statut: string;
  niveau?: { id: string; code: string; libelle: string };
  classe?: { id: string; nom: string };
}

export interface Eleve {
  id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance: string;
  lieu_naissance: string | null;
  nationalite: string | null;
  adresse: string | null;
  photo_url: string | null;
  groupe_sanguin: string | null;
  allergies: string | null;
  statut: string;
  created_at: string;
  tuteurs: Tuteur[];
  inscriptions: Inscription[];
}

export interface EleveListItem {
  id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance: string;
  statut: string;
  niveau_libelle: string | null;
  niveau_code: string | null;
  classe_nom: string | null;
}

export interface EleveListResponse {
  items: EleveListItem[];
  total: number;
}

export interface CreateEleveRequest {
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance: string;
  lieu_naissance?: string;
  nationalite?: string;
  adresse?: string;
  groupe_sanguin?: string;
  allergies?: string;
  niveau_id: string;
  tuteurs: {
    type: string;
    nom: string;
    prenoms: string;
    telephone: string;
    profession?: string;
    adresse?: string;
    email?: string;
  }[];
}

export interface TransfertEntrantRequest extends CreateEleveRequest {
  ecole_origine: string;
  date_transfert?: string;
  observations?: string;
}
