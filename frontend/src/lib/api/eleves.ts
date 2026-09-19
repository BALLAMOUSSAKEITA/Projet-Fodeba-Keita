import type {
  CreateEleveRequest,
  Eleve,
  EleveListResponse,
  TransfertEntrantRequest,
} from "@/types/eleve";
import type { EffectifStats, HistoriqueScolaire } from "@/types/classe";
import { apiDownload, apiFetch } from "./client";

export async function listEleves(
  token: string,
  params?: {
    search?: string;
    sexe?: string;
    niveau_id?: string;
    classe_id?: string;
    statut?: string;
  },
) {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.sexe) query.set("sexe", params.sexe);
  if (params?.niveau_id) query.set("niveau_id", params.niveau_id);
  if (params?.classe_id) query.set("classe_id", params.classe_id);
  if (params?.statut) query.set("statut", params.statut);
  const qs = query.toString() ? `?${query.toString()}` : "";
  return apiFetch<EleveListResponse>(`/api/v1/eleves${qs}`, {}, token);
}

export async function getEleve(token: string, id: string) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}`, {}, token);
}

export async function createEleve(token: string, data: CreateEleveRequest) {
  return apiFetch<Eleve>("/api/v1/eleves", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function createTransfertEntrant(token: string, data: TransfertEntrantRequest) {
  return apiFetch<Eleve>("/api/v1/eleves/transfert-entrant", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function updateEleve(token: string, id: string, data: Partial<CreateEleveRequest>) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}

export async function reinscrireEleve(token: string, id: string, niveauId: string) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}/reinscrire`, {
    method: "POST",
    body: JSON.stringify({ niveau_id: niveauId }),
  }, token);
}

export async function affecterClasse(token: string, id: string, classeId: string) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}/affecter-classe`, {
    method: "POST",
    body: JSON.stringify({ classe_id: classeId }),
  }, token);
}

export async function transfertSortant(
  token: string,
  id: string,
  data: { ecole_destination: string; motif?: string; date_transfert?: string },
) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}/transfert-sortant`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function desactiverEleve(
  token: string,
  id: string,
  data: { motif: string; date_inactivite?: string },
) {
  return apiFetch<Eleve>(`/api/v1/eleves/${id}/desactiver`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function getHistorique(token: string, id: string) {
  return apiFetch<HistoriqueScolaire>(`/api/v1/eleves/${id}/historique`, {}, token);
}

export async function getStatsEffectifs(token: string) {
  return apiFetch<EffectifStats>("/api/v1/eleves/statistiques/effectifs", {}, token);
}

export async function downloadAttestationScolarite(token: string, id: string, matricule: string) {
  await apiDownload(`/api/v1/eleves/${id}/attestation/scolarite`, token, `attestation_${matricule}.pdf`);
}

export async function downloadCertificatTransfert(
  token: string,
  id: string,
  matricule: string,
  ecole: string,
) {
  const q = new URLSearchParams({ ecole });
  await apiDownload(
    `/api/v1/eleves/${id}/attestation/transfert?${q.toString()}`,
    token,
    `transfert_${matricule}.pdf`,
  );
}
