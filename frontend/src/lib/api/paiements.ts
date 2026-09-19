import type { CaisseJournaliere, ImpayeItem, Paiement, SituationEleve, TrancheOption } from "@/types/paiements";
import { apiDownload, apiFetch } from "./client";

const base = "/api/v1/paiements";

export async function createPaiement(
  token: string,
  data: {
    eleve_id: string;
    type_frais_id: string;
    tranche_id?: string;
    montant: number;
    mode_paiement: string;
    reference_externe?: string;
    date_paiement?: string;
    remise_montant?: number;
  },
) {
  return apiFetch<Paiement>(base, { method: "POST", body: JSON.stringify(data) }, token);
}

export async function getSituationEleve(token: string, eleveId: string) {
  return apiFetch<SituationEleve>(`${base}/eleve/${eleveId}/situation`, {}, token);
}

export async function listImpayes(token: string, classeId?: string) {
  const q = classeId ? `?classe_id=${classeId}` : "";
  return apiFetch<ImpayeItem[]>(`${base}/impayes/liste${q}`, {}, token);
}

export async function relancerImpaye(
  token: string,
  data: { eleve_id: string; canal: string; message?: string },
) {
  return apiFetch<{ id: string }>(`${base}/impayes/relance`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function getCaisseJournaliere(token: string, date: string) {
  return apiFetch<CaisseJournaliere>(`${base}/caisse/journaliere?date=${date}`, {}, token);
}

export async function listTranches(token: string, anneeId: string, typeFraisId: string) {
  return apiFetch<TrancheOption[]>(
    `${base}/tranches?annee_scolaire_id=${anneeId}&type_frais_id=${typeFraisId}`,
    {},
    token,
  );
}

export async function downloadRecuPdf(token: string, paiementId: string, filename: string) {
  await apiDownload(`${base}/${paiementId}/recu/pdf`, token, filename);
}

export async function annulerPaiement(token: string, paiementId: string, motif: string) {
  return apiFetch<Paiement>(
    `${base}/${paiementId}/annuler`,
    { method: "POST", body: JSON.stringify({ motif }) },
    token,
  );
}
