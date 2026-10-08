/** Coordonnées officielles GSP Fodeba Keita (alignées backend / PDF). */
export const ETABLISSEMENT_NOM = "Groupe Scolaire Privé Fodeba Keita";
export const ETABLISSEMENT_ADRESSE = "Commune de Matam, Conakry";
export const ETABLISSEMENT_COMMUNE = "Matam";

export function formatEtablissementAdresse(adresse?: string | null, commune?: string | null): string {
  if (adresse?.trim()) return adresse.trim();
  if (commune?.trim()) return `Commune de ${commune.trim()}, Conakry`;
  return ETABLISSEMENT_ADRESSE;
}
