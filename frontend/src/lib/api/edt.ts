import type { ConflitsResponse, Creneau, GrilleEdt, SeanceEdt } from "@/types/edt";
import { apiDownload, apiFetch } from "./client";

export async function listCreneaux(token: string) {
  return apiFetch<Creneau[]>("/api/v1/emploi-du-temps/creneaux", {}, token);
}

export async function getGrilleClasse(token: string, classeId: string) {
  return apiFetch<GrilleEdt>(`/api/v1/emploi-du-temps/classe/${classeId}`, {}, token);
}

export async function getGrilleEnseignant(token: string, personnelId: string) {
  return apiFetch<GrilleEdt>(`/api/v1/emploi-du-temps/enseignant/${personnelId}`, {}, token);
}

export async function listConflits(token: string) {
  return apiFetch<ConflitsResponse>("/api/v1/emploi-du-temps/conflits", {}, token);
}

export async function createSeance(
  token: string,
  data: {
    classe_id: string;
    creneau_id: string;
    jour_semaine: number;
    matiere_id: string;
    personnel_id: string;
    salle?: string;
  },
) {
  return apiFetch<SeanceEdt>("/api/v1/emploi-du-temps/seances", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteSeance(token: string, seanceId: string) {
  return apiFetch<void>(`/api/v1/emploi-du-temps/seances/${seanceId}`, {
    method: "DELETE",
  }, token);
}

export async function downloadEdtPdf(token: string, classeId: string, filename: string) {
  await apiDownload(`/api/v1/emploi-du-temps/classe/${classeId}/export/pdf`, token, filename);
}

export async function downloadEdtExcel(token: string, classeId: string, filename: string) {
  await apiDownload(`/api/v1/emploi-du-temps/classe/${classeId}/export/excel`, token, filename);
}
