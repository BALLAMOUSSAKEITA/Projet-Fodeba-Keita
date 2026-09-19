import type { ClasseEffectif, ClasseElevesResponse } from "@/types/classe";
import { apiDownload, apiFetch } from "./client";

export async function listClasseEffectifs(token: string) {
  return apiFetch<ClasseEffectif[]>("/api/v1/classes/effectifs", {}, token);
}

export async function getClasseEleves(token: string, classeId: string) {
  return apiFetch<ClasseElevesResponse>(`/api/v1/classes/${classeId}/eleves`, {}, token);
}

export async function downloadListeClassePdf(token: string, classeId: string, filename: string) {
  await apiDownload(`/api/v1/classes/${classeId}/liste-pdf`, token, filename);
}
