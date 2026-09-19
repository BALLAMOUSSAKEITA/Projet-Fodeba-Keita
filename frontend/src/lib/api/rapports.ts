import type {
  DashboardKPI,
  Graphiques,
  RapportEffectifs,
  RapportFinancier,
  RapportPedagogique,
  RapportPresence,
  StatistiquesAnnuelles,
} from "@/types/rapports";
import { apiDownload, apiFetch } from "./client";

const base = "/api/v1/rapports";

export async function getDashboardKPI(token: string) {
  return apiFetch<DashboardKPI>(`${base}/dashboard/kpi`, {}, token);
}

export async function getRapportEffectifs(token: string) {
  return apiFetch<RapportEffectifs>(`${base}/effectifs`, {}, token);
}

export async function getRapportFinancier(
  token: string,
  dateDebut: string,
  dateFin: string,
  anneeScolaireId?: string,
) {
  const params = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
  if (anneeScolaireId) params.set("annee_scolaire_id", anneeScolaireId);
  return apiFetch<RapportFinancier>(`${base}/financier?${params}`, {}, token);
}

export async function getRapportPedagogique(token: string, periodeId?: string) {
  const q = periodeId ? `?periode_id=${periodeId}` : "";
  return apiFetch<RapportPedagogique>(`${base}/pedagogique${q}`, {}, token);
}

export async function getRapportPresence(token: string, dateDebut: string, dateFin: string) {
  return apiFetch<RapportPresence>(
    `${base}/presence?date_debut=${dateDebut}&date_fin=${dateFin}`,
    {},
    token,
  );
}

export async function getStatistiquesAnnuelles(token: string) {
  return apiFetch<StatistiquesAnnuelles>(`${base}/annuel`, {}, token);
}

export async function getGraphiques(token: string) {
  return apiFetch<Graphiques>(`${base}/graphiques`, {}, token);
}

export async function downloadRapportCsv(token: string, type: "effectifs" | "financier", dates?: { debut: string; fin: string; anneeId?: string }) {
  let path = `${base}/export/csv?type=${type}`;
  if (type === "financier" && dates) {
    path += `&date_debut=${dates.debut}&date_fin=${dates.fin}`;
    if (dates.anneeId) path += `&annee_scolaire_id=${dates.anneeId}`;
  }
  await apiDownload(path, token, `rapport_${type}.csv`);
}

export async function downloadRapportExcel(
  token: string,
  type: "effectifs" | "financier" | "pedagogique" | "annuel",
  dates?: { debut: string; fin: string; anneeId?: string },
) {
  let path = `${base}/export/excel?type=${type}`;
  if (type === "financier" && dates) {
    path += `&date_debut=${dates.debut}&date_fin=${dates.fin}`;
    if (dates.anneeId) path += `&annee_scolaire_id=${dates.anneeId}`;
  }
  await apiDownload(path, token, `rapport_${type}.xlsx`);
}

export async function downloadRapportPdf(
  token: string,
  type: "effectifs" | "financier" | "annuel",
  dates?: { debut: string; fin: string; anneeId?: string },
) {
  let path = `${base}/export/pdf?type=${type}`;
  if (type === "financier" && dates) {
    path += `&date_debut=${dates.debut}&date_fin=${dates.fin}`;
    if (dates.anneeId) path += `&annee_scolaire_id=${dates.anneeId}`;
  }
  await apiDownload(path, token, `rapport_${type}.pdf`);
}
