import type { AnneeScolaire } from "@/types/parametrage";

export const ANNEES_CLASSE_OPTIONS = ["2026-2027", "2027-2028", "2028-2029", "2029-2030"] as const;

export const DEFAULT_ANNEE_CLASSE = "2026-2027";

export function anneesForClassesSelect(all: AnneeScolaire[]): AnneeScolaire[] {
  return ANNEES_CLASSE_OPTIONS.map((libelle) => all.find((a) => a.libelle === libelle)).filter(
    (a): a is AnneeScolaire => a != null,
  );
}

export function defaultAnneeClasseId(all: AnneeScolaire[]): string {
  const options = anneesForClassesSelect(all);
  const preferred = options.find((a) => a.libelle === DEFAULT_ANNEE_CLASSE);
  return (preferred ?? options[0] ?? all.find((a) => a.is_active) ?? all[0])?.id ?? "";
}
