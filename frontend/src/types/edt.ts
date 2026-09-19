export interface Creneau {
  id: string;
  libelle: string;
  heure_debut: string;
  heure_fin: string;
  ordre: number;
  annee_scolaire_id: string;
}

export interface SeanceEdt {
  id: string;
  classe_id: string;
  creneau_id: string;
  jour_semaine: number;
  matiere_id: string;
  personnel_id: string;
  salle: string | null;
  matiere?: { id: string; code: string; libelle: string };
  personnel?: { id: string; nom: string; prenoms: string };
  classe?: { id: string; nom: string };
}

export interface LigneGrille {
  creneau: Creneau;
  cellules: (SeanceEdt | null)[];
}

export interface ConflitEdt {
  type: string;
  message: string;
  seance_ids: string[];
}

export interface GrilleEdt {
  titre: string;
  jours: string[];
  lignes: LigneGrille[];
  conflits: ConflitEdt[];
}

export interface ConflitsResponse {
  items: ConflitEdt[];
  total: number;
}
