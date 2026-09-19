import type { AvanceSalaire, BulletinPaie, MasseSalariale, PeriodePaie } from "@/types/paie";
import { apiDownload, apiFetch } from "./client";

const base = "/api/v1/paie";

export async function listPeriodesPaie(token: string) {
  return apiFetch<PeriodePaie[]>(`${base}/periodes`, {}, token);
}

export async function createPeriodePaie(token: string, annee: number, mois: number) {
  return apiFetch<PeriodePaie>(`${base}/periodes`, {
    method: "POST",
    body: JSON.stringify({ annee, mois }),
  }, token);
}

export async function genererPaie(token: string, periodeId: string) {
  return apiFetch<BulletinPaie[]>(`${base}/periodes/${periodeId}/generer`, { method: "POST" }, token);
}

export async function listBulletinsPaie(token: string, periodeId: string) {
  return apiFetch<BulletinPaie[]>(`${base}/bulletins?periode_paie_id=${periodeId}`, {}, token);
}

export async function getMasseSalariale(token: string, periodeId: string) {
  return apiFetch<MasseSalariale>(`${base}/masse-salariale?periode_paie_id=${periodeId}`, {}, token);
}

export async function validerBulletinPaie(token: string, bulletinId: string) {
  return apiFetch<BulletinPaie>(`${base}/bulletins/${bulletinId}/valider`, { method: "POST" }, token);
}

export async function payerBulletinPaie(token: string, bulletinId: string) {
  return apiFetch<BulletinPaie>(`${base}/bulletins/${bulletinId}/payer`, { method: "POST" }, token);
}

export async function downloadBulletinPaiePdf(token: string, bulletinId: string, filename: string) {
  await apiDownload(`${base}/bulletins/${bulletinId}/pdf`, token, filename);
}

export async function listAvances(token: string) {
  return apiFetch<AvanceSalaire[]>(`${base}/avances`, {}, token);
}

export async function createAvance(
  token: string,
  data: { personnel_id: string; montant: number; date_avance: string; motif?: string },
) {
  return apiFetch<AvanceSalaire>(`${base}/avances`, { method: "POST", body: JSON.stringify(data) }, token);
}

export async function getMesBulletins(token: string) {
  return apiFetch<BulletinPaie[]>(`${base}/mes-bulletins`, {}, token);
}
