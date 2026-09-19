export interface StatsPedagogiques {
  classe_id: string;
  classe_nom: string;
  periode_libelle: string;
  effectif: number;
  moyenne_classe: number | null;
  taux_reussite: number | null;
  meilleur_eleve: string | null;
  moins_bonne_moyenne: number | null;
}

export interface PalmaresItem {
  rang: number;
  eleve_id: string;
  nom: string;
  prenoms: string;
  matricule: string;
  moyenne_generale: number;
  appreciation: string | null;
}

export interface Palmares {
  classe_id: string;
  classe_nom: string;
  periode_libelle: string;
  items: PalmaresItem[];
}

export interface DecisionPassage {
  id: string;
  eleve_id: string;
  annee_scolaire_id: string;
  decision: string;
  observation: string | null;
}

export interface Competence {
  id: string;
  code: string;
  domaine: string;
  libelle: string;
  niveau_id: string;
  ordre: number;
}

export interface CompetenceGrilleRow {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  evaluations: Record<string, string | null>;
}

export interface CompetenceGrille {
  classe_id: string;
  classe_nom: string;
  periode_libelle: string;
  competences: Competence[];
  eleves: CompetenceGrilleRow[];
}

export type StatutCompetence = "acquis" | "en_cours" | "non_acquis" | "";

export type DecisionPassageType = "admis" | "redouble" | "exclu";
