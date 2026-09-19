import type {
  CompetenceGrille,
  DecisionPassage,
  Palmares,
  StatsPedagogiques,
} from "@/types/bulletins";
import { apiDownload, apiFetch } from "./client";

const base = "/api/v1/bulletins";

export async function getStatsPedagogiques(
  token: string,
  classeId: string,
  periodeId: string,
) {
  return apiFetch<StatsPedagogiques>(
    `${base}/classes/${classeId}/periodes/${periodeId}/stats`,
    {},
    token,
  );
}

export async function getPalmares(
  token: string,
  classeId: string,
  periodeId: string,
  limit = 20,
) {
  return apiFetch<Palmares>(
    `${base}/classes/${classeId}/periodes/${periodeId}/palmares?limit=${limit}`,
    {},
    token,
  );
}

export async function createDecisionPassage(
  token: string,
  data: {
    eleve_id: string;
    decision: string;
    observation?: string | null;
    annee_scolaire_id?: string;
  },
) {
  return apiFetch<DecisionPassage>(`${base}/decisions-passage`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function downloadBulletinElevePdf(
  token: string,
  eleveId: string,
  periodeId: string,
  filename: string,
) {
  await apiDownload(
    `${base}/eleve/${eleveId}/periodes/${periodeId}/pdf`,
    token,
    filename,
  );
}

export async function downloadBulletinsClassePdf(
  token: string,
  classeId: string,
  periodeId: string,
  filename: string,
) {
  await apiDownload(
    `${base}/classes/${classeId}/periodes/${periodeId}/pdf`,
    token,
    filename,
  );
}

export async function downloadBulletinAnnuelPdf(
  token: string,
  eleveId: string,
  filename: string,
) {
  await apiDownload(`${base}/eleve/${eleveId}/annuel/pdf`, token, filename);
}

export async function getGrilleCompetences(
  token: string,
  classeId: string,
  periodeId: string,
) {
  return apiFetch<CompetenceGrille>(
    `${base}/classes/${classeId}/periodes/${periodeId}/competences`,
    {},
    token,
  );
}

export async function saveGrilleCompetences(
  token: string,
  classeId: string,
  periodeId: string,
  items: {
    eleve_id: string;
    evaluations: { competence_id: string; statut: string; appreciation?: string | null }[];
  }[],
) {
  return apiFetch<CompetenceGrille>(
    `${base}/classes/${classeId}/periodes/${periodeId}/competences`,
    { method: "PUT", body: JSON.stringify(items) },
    token,
  );
}

export async function downloadBulletinMaternellePdf(
  token: string,
  eleveId: string,
  periodeId: string,
  filename: string,
) {
  await apiDownload(
    `${base}/eleve/${eleveId}/periodes/${periodeId}/maternelle/pdf`,
    token,
    filename,
  );
}
