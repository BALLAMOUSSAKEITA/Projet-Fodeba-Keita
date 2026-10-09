/** Coordonnées officielles GSP Fodeba Keita (alignées backend / PDF). */
export const ETABLISSEMENT_NOM = "Groupe Scolaire Privé Fodeba Keita";
export const ETABLISSEMENT_ADRESSE = "Commune de Matam, Conakry";
export const ETABLISSEMENT_COMMUNE = "Matam";
export const ETABLISSEMENT_TELEPHONE = "+224626137290";
export const ETABLISSEMENT_TELEPHONE_AFFICHAGE = "626 137 290";

export function formatTelephoneAffichage(telephone?: string | null): string {
  if (!telephone?.trim()) return ETABLISSEMENT_TELEPHONE_AFFICHAGE;
  const raw = telephone.trim().replace(/\s/g, "").replace(/-/g, "");
  let digits = raw.startsWith("+224") ? raw.slice(4) : raw.startsWith("224") ? raw.slice(3) : raw.replace(/^\+/, "");
  if (/^\d{9}$/.test(digits)) {
    return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  }
  return telephone.trim();
}

export function formatEtablissementAdresse(adresse?: string | null, commune?: string | null): string {
  if (adresse?.trim()) return adresse.trim();
  if (commune?.trim()) return `Commune de ${commune.trim()}, Conakry`;
  return ETABLISSEMENT_ADRESSE;
}
