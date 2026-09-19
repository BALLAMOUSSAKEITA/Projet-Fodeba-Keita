import type {
  Evaluation,
  GrilleNotes,
  MoyennesClasse,
  TypeEvaluation,
} from "@/types/notes";
import { apiFetch } from "./client";

export async function listTypesEvaluation(token: string) {
  return apiFetch<TypeEvaluation[]>("/api/v1/notes/types-evaluation", {}, token);
}

export async function listEvaluations(
  token: string,
  params: { classe_id: string; matiere_id: string; periode_id: string },
) {
  const q = new URLSearchParams(params);
  return apiFetch<Evaluation[]>(`/api/v1/notes/evaluations?${q}`, {}, token);
}

export async function createEvaluation(
  token: string,
  data: {
    libelle: string;
    classe_id: string;
    matiere_id: string;
    periode_id: string;
    type_evaluation_id: string;
    coefficient?: number;
  },
) {
  return apiFetch<Evaluation>("/api/v1/notes/evaluations", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function getGrilleNotes(token: string, evaluationId: string) {
  return apiFetch<GrilleNotes>(`/api/v1/notes/evaluations/${evaluationId}/grille`, {}, token);
}

export async function saveNotes(
  token: string,
  evaluationId: string,
  notes: { eleve_id: string; valeur?: number | null; is_absent?: boolean; appreciation_libre?: string }[],
) {
  return apiFetch<GrilleNotes>(`/api/v1/notes/evaluations/${evaluationId}/notes`, {
    method: "PUT",
    body: JSON.stringify({ notes }),
  }, token);
}

export async function getMoyennesClasse(token: string, classeId: string, periodeId: string) {
  return apiFetch<MoyennesClasse>(
    `/api/v1/notes/classes/${classeId}/periodes/${periodeId}/moyennes`,
    {},
    token,
  );
}

export async function validerNotes(token: string, classeId: string, periodeId: string) {
  return apiFetch<{ verrouille: boolean }>(
    `/api/v1/notes/classes/${classeId}/periodes/${periodeId}/valider`,
    { method: "POST" },
    token,
  );
}
