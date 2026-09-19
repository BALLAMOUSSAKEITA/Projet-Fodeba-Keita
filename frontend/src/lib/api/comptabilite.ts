import type {
  BudgetSuivi,
  CategorieDepense,
  CompteTresorerie,
  Depense,
  Ecriture,
  RapportFinancier,
  Tresorerie,
} from "@/types/comptabilite";
import { apiDownload, apiFetch } from "./client";

const base = "/api/v1/comptabilite";

export async function listCategoriesDepense(token: string) {
  return apiFetch<CategorieDepense[]>(`${base}/categories`, {}, token);
}

export async function listComptesTresorerie(token: string) {
  return apiFetch<CompteTresorerie[]>(`${base}/comptes`, {}, token);
}

export async function getTresorerie(token: string) {
  return apiFetch<Tresorerie>(`${base}/tresorerie`, {}, token);
}

export async function listDepenses(token: string, statut?: string, anneeScolaireId?: string) {
  const params = new URLSearchParams();
  if (statut) params.set("statut", statut);
  if (anneeScolaireId) params.set("annee_scolaire_id", anneeScolaireId);
  const q = params.toString();
  return apiFetch<Depense[]>(`${base}/depenses${q ? `?${q}` : ""}`, {}, token);
}

export async function createDepense(
  token: string,
  data: {
    categorie_id: string;
    libelle: string;
    montant: number;
    date_depense: string;
    compte_tresorerie_id: string;
    annee_scolaire_id?: string;
    reference_piece?: string;
  },
) {
  return apiFetch<Depense>(`${base}/depenses`, { method: "POST", body: JSON.stringify(data) }, token);
}

export async function soumettreDepense(token: string, depenseId: string) {
  return apiFetch<Depense>(`${base}/depenses/${depenseId}/soumettre`, { method: "POST" }, token);
}

export async function validerDepense(token: string, depenseId: string) {
  return apiFetch<Depense>(`${base}/depenses/${depenseId}/valider`, { method: "POST" }, token);
}

export async function refuserDepense(token: string, depenseId: string, motif: string) {
  return apiFetch<Depense>(
    `${base}/depenses/${depenseId}/refuser`,
    { method: "POST", body: JSON.stringify({ motif }) },
    token,
  );
}

export async function getBudgetSuivi(token: string, anneeScolaireId: string) {
  return apiFetch<BudgetSuivi>(`${base}/budget/suivi?annee_scolaire_id=${anneeScolaireId}`, {}, token);
}

export async function listJournal(token: string, dateDebut: string, dateFin: string) {
  return apiFetch<Ecriture[]>(
    `${base}/journal?date_debut=${dateDebut}&date_fin=${dateFin}`,
    {},
    token,
  );
}

export async function getRapportFinancier(
  token: string,
  dateDebut: string,
  dateFin: string,
  anneeScolaireId?: string,
) {
  const params = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
  if (anneeScolaireId) params.set("annee_scolaire_id", anneeScolaireId);
  return apiFetch<RapportFinancier>(`${base}/rapports/financier?${params}`, {}, token);
}

export async function downloadRapportCsv(
  token: string,
  dateDebut: string,
  dateFin: string,
  anneeScolaireId?: string,
) {
  const params = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
  if (anneeScolaireId) params.set("annee_scolaire_id", anneeScolaireId);
  await apiDownload(`${base}/export/csv?${params}`, token, "rapport_financier.csv");
}

export async function downloadRapportExcel(
  token: string,
  dateDebut: string,
  dateFin: string,
  anneeScolaireId?: string,
) {
  const params = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
  if (anneeScolaireId) params.set("annee_scolaire_id", anneeScolaireId);
  await apiDownload(`${base}/export/excel?${params}`, token, "rapport_financier.xlsx");
}
