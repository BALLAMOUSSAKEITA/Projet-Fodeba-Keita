import type { EnfantItem, PortailResume } from "@/types/communication";
import { apiFetch } from "./client";

const base = "/api/v1/portail";

export async function listMesEnfants(token: string) {
  return apiFetch<EnfantItem[]>(`${base}/mes-enfants`, {}, token);
}

export async function getResumeEnfant(token: string, eleveId: string) {
  return apiFetch<PortailResume>(`${base}/enfants/${eleveId}/resume`, {}, token);
}
