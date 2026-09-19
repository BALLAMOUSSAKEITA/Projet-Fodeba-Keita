import type {
  CreatePersonnelRequest,
  Personnel,
  PersonnelListResponse,
} from "@/types/personnel";
import { apiFetch } from "./client";

export async function listPersonnel(
  token: string,
  params?: { search?: string; categorie?: string; statut?: string },
) {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.categorie) query.set("categorie", params.categorie);
  if (params?.statut) query.set("statut", params.statut);
  const qs = query.toString() ? `?${query.toString()}` : "";
  return apiFetch<PersonnelListResponse>(`/api/v1/personnel${qs}`, {}, token);
}

export async function getPersonnel(token: string, id: string) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}`, {}, token);
}

export async function createPersonnel(token: string, data: CreatePersonnelRequest) {
  return apiFetch<Personnel>("/api/v1/personnel", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function addDiplome(
  token: string,
  id: string,
  data: { libelle: string; etablissement?: string; annee_obtention?: number; niveau?: string },
) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/diplomes`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function addContrat(
  token: string,
  id: string,
  data: {
    type_contrat: string;
    date_debut: string;
    date_fin?: string;
    salaire_mensuel?: number;
  },
) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/contrats`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function addAffectation(
  token: string,
  id: string,
  data: { classe_id: string; matiere_id: string },
) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/affectations`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function setTitulaire(token: string, id: string, classeId: string) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/titulaire`, {
    method: "POST",
    body: JSON.stringify({ classe_id: classeId }),
  }, token);
}

export async function addConge(
  token: string,
  id: string,
  data: { type: string; date_debut: string; date_fin: string; motif?: string },
) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/conges`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function updateCongeStatut(
  token: string,
  id: string,
  congeId: string,
  statut: string,
) {
  return apiFetch<Personnel>(`/api/v1/personnel/${id}/conges/${congeId}`, {
    method: "PATCH",
    body: JSON.stringify({ statut }),
  }, token);
}
