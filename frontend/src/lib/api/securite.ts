import type { AuditLog, HistoriqueNote, HistoriquePaiement, LoginLog, SauvegardeStatus } from "@/types/securite";
import { apiFetch } from "./client";

const base = "/api/v1/securite";

export async function listAuditLogs(token: string, resourceType?: string) {
  const q = resourceType ? `?resource_type=${resourceType}` : "";
  return apiFetch<AuditLog[]>(`${base}/audit${q}`, {}, token);
}

export async function listHistoriqueNotes(token: string, eleveId?: string) {
  const q = eleveId ? `?eleve_id=${eleveId}` : "";
  return apiFetch<HistoriqueNote[]>(`${base}/historique/notes${q}`, {}, token);
}

export async function listHistoriquePaiements(token: string, eleveId?: string) {
  const q = eleveId ? `?eleve_id=${eleveId}` : "";
  return apiFetch<HistoriquePaiement[]>(`${base}/historique/paiements${q}`, {}, token);
}

export async function listConnexions(token: string) {
  return apiFetch<LoginLog[]>(`${base}/connexions`, {}, token);
}

export async function getSauvegardeStatus(token: string) {
  return apiFetch<SauvegardeStatus>(`${base}/sauvegarde`, {}, token);
}

export async function cloturerAnnee(token: string, anneeId: string) {
  return apiFetch<{ id: string; libelle: string; statut: string }>(
    `${base}/annees/${anneeId}/cloturer`,
    { method: "POST" },
    token,
  );
}
