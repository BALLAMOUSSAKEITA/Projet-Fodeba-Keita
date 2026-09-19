export interface PresenceEleveRow {
  presence_id: string | null;
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  statut: string;
  retard_minutes: number | null;
  motif: string | null;
  justification: string | null;
  justification_statut: string | null;
}

export interface AppelPresence {
  appel_id: string | null;
  classe_id: string;
  classe_nom: string;
  date: string;
  remarque: string | null;
  eleves: PresenceEleveRow[];
}

export interface EleveRecapItem {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  jours_absents: number;
  jours_retards: number;
  minutes_retard_total: number;
  jours_excuses: number;
  absences_non_justifiees: number;
}

export interface ClasseRecap {
  classe_id: string;
  classe_nom: string;
  date_debut: string;
  date_fin: string;
  effectif: number;
  eleves: EleveRecapItem[];
}

export interface Incident {
  id: string;
  eleve_id: string;
  eleve_nom: string;
  eleve_prenoms: string;
  classe_id: string | null;
  classe_nom: string | null;
  date: string;
  type: string;
  description: string;
  sanction: string | null;
}

export type StatutPresence = "present" | "absent" | "retard" | "excuse";
