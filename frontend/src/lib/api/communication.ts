import type { Annonce, HistoriqueCommunication, ModeleMessage } from "@/types/communication";
import { apiFetch } from "./client";

const base = "/api/v1/communication";

export async function listAnnonces(
  token: string,
  params?: { audience?: string; publiees_seulement?: boolean },
) {
  const q = new URLSearchParams();
  if (params?.audience) q.set("audience", params.audience);
  if (params?.publiees_seulement) q.set("publiees_seulement", "true");
  const query = q.toString();
  return apiFetch<Annonce[]>(`${base}/annonces${query ? `?${query}` : ""}`, {}, token);
}

export async function createAnnonce(
  token: string,
  data: { titre: string; contenu: string; audience: string; date_expiration?: string },
  publier = false,
) {
  return apiFetch<Annonce>(
    `${base}/annonces?publier=${publier}`,
    { method: "POST", body: JSON.stringify(data) },
    token,
  );
}

export async function publierAnnonce(token: string, annonceId: string) {
  return apiFetch<Annonce>(`${base}/annonces/${annonceId}/publier`, { method: "POST" }, token);
}

export async function archiverAnnonce(token: string, annonceId: string) {
  return apiFetch<Annonce>(`${base}/annonces/${annonceId}/archiver`, { method: "POST" }, token);
}

export async function listModelesMessages(token: string) {
  return apiFetch<ModeleMessage[]>(`${base}/modeles`, {}, token);
}

export async function envoyerMessage(
  token: string,
  data: {
    modele_id?: string;
    canal: string;
    destinataire: string;
    sujet: string;
    corps: string;
    eleve_id?: string;
  },
) {
  return apiFetch<HistoriqueCommunication>(
    `${base}/envoyer`,
    { method: "POST", body: JSON.stringify(data) },
    token,
  );
}

export async function listHistoriqueCommunications(token: string) {
  return apiFetch<HistoriqueCommunication[]>(`${base}/historique`, {}, token);
}
