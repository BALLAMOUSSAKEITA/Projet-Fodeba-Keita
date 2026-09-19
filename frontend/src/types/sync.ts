export interface SyncClasseItem {
  id: string;
  nom: string;
  capacite_max: number;
  salle: string | null;
  niveau_code: string | null;
}

export interface SyncEleveItem {
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

export interface SyncPullResponse {
  server_time: string;
  eleves: SyncEleveItem[];
  eleves_total: number;
  classes: SyncClasseItem[];
  notes_changes: unknown[];
  presences_changes: unknown[];
  paiements_changes: unknown[];
}

export interface SyncPushResultItem {
  client_id: string;
  status: "applied" | "conflict" | "error" | "duplicate";
  entity_type: string;
  server_id: string | null;
  message: string | null;
}

export interface SyncPushResponse {
  results: SyncPushResultItem[];
  applied: number;
  conflicts: number;
  errors: number;
}

export type SyncEntityType = "notes" | "presence" | "paiement";

export interface SyncQueueItem {
  id: string;
  entity_type: SyncEntityType;
  client_updated_at: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export type SyncStatus = "idle" | "syncing" | "offline" | "error";
