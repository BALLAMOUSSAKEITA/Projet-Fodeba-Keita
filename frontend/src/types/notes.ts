export interface TypeEvaluation {
  id: string;
  code: string;
  libelle: string;
  coefficient_defaut: number;
}

export interface Evaluation {
  id: string;
  libelle: string;
  classe_id: string;
  matiere_id: string;
  periode_id: string;
  type_evaluation_id: string;
  coefficient: number;
  type_evaluation?: TypeEvaluation;
}

export interface Note {
  id: string;
  eleve_id: string;
  valeur: number | null;
  is_absent: boolean;
  appreciation_libre: string | null;
  appreciation_auto: string | null;
}

export interface EleveNoteRow {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  note: Note | null;
}

export interface GrilleNotes {
  evaluation: Evaluation;
  verrouille: boolean;
  eleves: EleveNoteRow[];
  bareme_max: number;
  echelle: string;
}

export interface MoyenneMatiere {
  matiere_id: string;
  matiere_code: string;
  matiere_libelle: string;
  coefficient_matiere: number;
  moyenne: number | null;
  appreciation_auto: string | null;
}

export interface EleveMoyennes {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  moyennes_matieres: MoyenneMatiere[];
  moyenne_generale: number | null;
  appreciation_generale: string | null;
  rang: number | null;
}

export interface MoyennesClasse {
  classe_id: string;
  classe_nom: string;
  periode_id: string;
  periode_libelle: string;
  verrouille: boolean;
  eleves: EleveMoyennes[];
}
