export interface PersonnelListItem {
  id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  sexe: string;
  telephone: string;
  email: string | null;
  categorie: string;
  fonction: string | null;
  specialite: string | null;
  statut: string;
}

export interface PersonnelListResponse {
  items: PersonnelListItem[];
  total: number;
}

export interface Diplome {
  id: string;
  personnel_id: string;
  libelle: string;
  etablissement: string | null;
  annee_obtention: number | null;
  niveau: string | null;
}

export interface Contrat {
  id: string;
  personnel_id: string;
  type_contrat: string;
  date_debut: string;
  date_fin: string | null;
  salaire_mensuel: number | null;
  statut: string;
}

export interface Affectation {
  id: string;
  personnel_id: string;
  classe_id: string;
  matiere_id: string;
  annee_scolaire_id: string;
  classe?: { id: string; nom: string };
  matiere?: { id: string; code: string; libelle: string };
}

export interface Conge {
  id: string;
  personnel_id: string;
  type: string;
  date_debut: string;
  date_fin: string;
  motif: string | null;
  statut: string;
}

export interface Personnel {
  id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  sexe: string;
  date_naissance: string | null;
  telephone: string;
  email: string | null;
  adresse: string | null;
  categorie: string;
  fonction: string | null;
  specialite: string | null;
  date_embauche: string | null;
  statut: string;
  user_id: string | null;
  created_at: string;
  diplomes: Diplome[];
  contrats: Contrat[];
  affectations: Affectation[];
  conges: Conge[];
  classes_titulaire: { id: string; nom: string }[];
}

export interface CreatePersonnelRequest {
  nom: string;
  prenoms: string;
  sexe: string;
  telephone: string;
  categorie: string;
  date_naissance?: string;
  email?: string;
  adresse?: string;
  fonction?: string;
  specialite?: string;
  date_embauche?: string;
}
