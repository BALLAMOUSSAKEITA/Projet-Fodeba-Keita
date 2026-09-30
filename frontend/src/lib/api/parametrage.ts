import type {
  AnneeScolaire,
  Bareme,
  CalendrierEntry,
  Classe,
  Etablissement,
  Matiere,
  Niveau,
  ParametrageStatut,
  Periode,
  Referentiel,
  TypeFrais,
} from "@/types/parametrage";
import { apiFetch } from "./client";

const base = "/api/v1/parametrage";

export async function getParametrageStatut(token: string) {
  return apiFetch<ParametrageStatut>(`${base}/statut`, {}, token);
}

export async function getEtablissement(token: string) {
  return apiFetch<Etablissement>(`${base}/etablissement`, {}, token);
}

export async function updateEtablissement(token: string, data: Partial<Etablissement>) {
  return apiFetch<Etablissement>(`${base}/etablissement`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function getAnneeActive(token: string) {
  return apiFetch<AnneeScolaire>(`${base}/annees-scolaires/active`, {}, token);
}

export async function listAnnees(token: string) {
  return apiFetch<AnneeScolaire[]>(`${base}/annees-scolaires`, {}, token);
}

export async function listNiveaux(token: string) {
  return apiFetch<Niveau[]>(`${base}/niveaux`, {}, token);
}

export async function listClasses(token: string, anneeId?: string) {
  const q = anneeId ? `?annee_scolaire_id=${anneeId}` : "";
  return apiFetch<Classe[]>(`${base}/classes${q}`, {}, token);
}

export async function listMatieres(token: string) {
  return apiFetch<Matiere[]>(`${base}/matieres`, {}, token);
}

export async function listPeriodes(token: string, anneeId: string) {
  return apiFetch<Periode[]>(`${base}/periodes?annee_scolaire_id=${anneeId}`, {}, token);
}

export async function getBareme(token: string, anneeId: string) {
  return apiFetch<Bareme>(`${base}/bareme/${anneeId}`, {}, token);
}

export async function updateBareme(token: string, anneeId: string, data: Partial<Bareme>) {
  return apiFetch<Bareme>(`${base}/bareme/${anneeId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function listTypesFrais(token: string) {
  return apiFetch<TypeFrais[]>(`${base}/types-frais`, {}, token);
}

export async function listCalendrier(token: string, anneeId: string) {
  return apiFetch<CalendrierEntry[]>(`${base}/calendrier?annee_scolaire_id=${anneeId}`, {}, token);
}

export async function listReferentiels(token: string, type: string) {
  return apiFetch<Referentiel[]>(`${base}/referentiels/${type}`, {}, token);
}

export async function updateClasse(token: string, id: string, data: Partial<Classe>) {
  return apiFetch<Classe>(`${base}/classes/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteClasse(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/classes/${id}`, { method: "DELETE" }, token);
}

export async function updateMatiere(
  token: string,
  id: string,
  data: Partial<{ libelle: string; coefficient_defaut: number }>,
) {
  return apiFetch<Matiere>(`${base}/matieres/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteMatiere(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/matieres/${id}`, { method: "DELETE" }, token);
}

export async function updateNiveau(token: string, id: string, data: Partial<Niveau>) {
  return apiFetch<Niveau>(`${base}/niveaux/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteNiveau(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/niveaux/${id}`, { method: "DELETE" }, token);
}

export async function updatePeriode(token: string, id: string, data: Partial<Periode>) {
  return apiFetch<Periode>(`${base}/periodes/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deletePeriode(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/periodes/${id}`, { method: "DELETE" }, token);
}

export async function updateTypeFrais(token: string, id: string, data: Partial<TypeFrais>) {
  return apiFetch<TypeFrais>(`${base}/types-frais/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteTypeFrais(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/types-frais/${id}`, { method: "DELETE" }, token);
}

export async function updateCalendrierEntry(token: string, id: string, data: Partial<CalendrierEntry>) {
  return apiFetch<CalendrierEntry>(`${base}/calendrier/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteCalendrierEntry(token: string, id: string) {
  return apiFetch<{ message: string }>(`${base}/calendrier/${id}`, { method: "DELETE" }, token);
}
