import type { AppelPresence, ClasseRecap, Incident, PresenceEleveRow } from "@/types/presences";
import { apiFetch } from "./client";

const base = "/api/v1/presences";

export async function getAppel(token: string, classeId: string, date: string) {
  return apiFetch<AppelPresence>(
    `${base}/classes/${classeId}/appels?date=${date}`,
    {},
    token,
  );
}

export async function saveAppel(
  token: string,
  classeId: string,
  date: string,
  presences: { eleve_id: string; statut: string; retard_minutes?: number | null; motif?: string | null }[],
  remarque?: string,
) {
  return apiFetch<AppelPresence>(
    `${base}/classes/${classeId}/appels?date=${date}`,
    { method: "PUT", body: JSON.stringify({ presences, remarque }) },
    token,
  );
}

export async function getClasseRecap(
  token: string,
  classeId: string,
  dateDebut: string,
  dateFin: string,
) {
  return apiFetch<ClasseRecap>(
    `${base}/classes/${classeId}/recapitulatif?date_debut=${dateDebut}&date_fin=${dateFin}`,
    {},
    token,
  );
}

export async function getAbsencesAJustifier(token: string, classeId?: string) {
  const q = classeId ? `?classe_id=${classeId}` : "";
  return apiFetch<PresenceEleveRow[]>(`${base}/absences-a-justifier${q}`, {}, token);
}

export async function reviewJustification(
  token: string,
  presenceId: string,
  statut: "acceptee" | "refusee",
  commentaire?: string,
) {
  return apiFetch<PresenceEleveRow>(
    `${base}/presences/${presenceId}/justification`,
    { method: "PATCH", body: JSON.stringify({ statut, commentaire }) },
    token,
  );
}

export async function submitJustification(
  token: string,
  presenceId: string,
  justification: string,
  accepter = false,
) {
  return apiFetch<PresenceEleveRow>(
    `${base}/presences/${presenceId}/justification`,
    { method: "POST", body: JSON.stringify({ justification, accepter }) },
    token,
  );
}

export async function listIncidents(
  token: string,
  params?: { classe_id?: string; eleve_id?: string },
) {
  const q = new URLSearchParams();
  if (params?.classe_id) q.set("classe_id", params.classe_id);
  if (params?.eleve_id) q.set("eleve_id", params.eleve_id);
  const qs = q.toString();
  return apiFetch<Incident[]>(`${base}/discipline${qs ? `?${qs}` : ""}`, {}, token);
}

export async function createIncident(
  token: string,
  data: {
    eleve_id: string;
    classe_id?: string;
    date: string;
    type: string;
    description: string;
    sanction?: string;
  },
) {
  return apiFetch<Incident>(`${base}/discipline`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}
