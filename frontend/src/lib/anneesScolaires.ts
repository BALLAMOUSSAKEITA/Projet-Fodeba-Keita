import type { AnneeScolaire } from "@/types/parametrage";

export const ANNEES_CLASSE_OPTIONS = ["2026-2027", "2027-2028", "2028-2029", "2029-2030"] as const;

export const DEFAULT_ANNEE_CLASSE = "2026-2027";

export function anneesForClassesSelect(all: AnneeScolaire[]): AnneeScolaire[] {
  const catalog = ANNEES_CLASSE_OPTIONS.map((libelle) => all.find((a) => a.libelle === libelle)).filter(
    (a): a is AnneeScolaire => a != null,
  );
  const catalogLabels = new Set(ANNEES_CLASSE_OPTIONS);
  const extras = all
    .filter((a) => !catalogLabels.has(a.libelle as (typeof ANNEES_CLASSE_OPTIONS)[number]))
    .sort((a, b) => a.libelle.localeCompare(b.libelle));
  return catalog.length > 0 ? [...catalog, ...extras] : [...all].sort((a, b) => a.libelle.localeCompare(b.libelle));
}

export function defaultAnneeClasseId(all: AnneeScolaire[]): string {
  const active = all.find((a) => a.is_active);
  if (active) return active.id;
  const options = anneesForClassesSelect(all);
  const preferred = options.find((a) => a.libelle === DEFAULT_ANNEE_CLASSE);
  return (preferred ?? options[0] ?? all[0])?.id ?? "";
}
