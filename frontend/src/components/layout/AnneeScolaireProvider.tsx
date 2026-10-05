"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { listAnnees } from "@/lib/api/parametrage";
import { anneesForClassesSelect, defaultAnneeClasseId } from "@/lib/anneesScolaires";
import { ApiError } from "@/lib/api/client";
import { getToken } from "@/lib/auth/session";
import type { AnneeScolaire } from "@/types/parametrage";

const STORAGE_KEY = "gsp_annee_scolaire_id";

type AnneeScolaireContextValue = {
  annees: AnneeScolaire[];
  anneeId: string;
  anneeLibelle: string;
  setAnneeId: (id: string) => void;
  loading: boolean;
};

const AnneeScolaireContext = createContext<AnneeScolaireContextValue | null>(null);

export function AnneeScolaireProvider({ children }: { children: ReactNode }) {
  const [annees, setAnnees] = useState<AnneeScolaire[]>([]);
  const [anneeId, setAnneeIdState] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    listAnnees(token)
      .then((all) => {
        const options = anneesForClassesSelect(all);
        const opts = options.length > 0 ? options : all;
        setAnnees(opts);
        const stored = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
        const fromStore = stored ? opts.find((a) => a.id === stored) : undefined;
        const id = fromStore?.id ?? defaultAnneeClasseId(opts.length ? opts : all);
        setAnneeIdState(id);
        if (id && typeof window !== "undefined") {
          localStorage.setItem(STORAGE_KEY, id);
        }
      })
      .catch((err) => {
        console.error(err instanceof ApiError ? err.message : "Années scolaires");
      })
      .finally(() => setLoading(false));
  }, []);

  const setAnneeId = useCallback((id: string) => {
    setAnneeIdState(id);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, id);
    }
  }, []);

  const anneeLibelle = useMemo(
    () => annees.find((a) => a.id === anneeId)?.libelle ?? "",
    [annees, anneeId],
  );

  const value = useMemo(
    () => ({ annees, anneeId, anneeLibelle, setAnneeId, loading }),
    [annees, anneeId, anneeLibelle, setAnneeId, loading],
  );

  return <AnneeScolaireContext.Provider value={value}>{children}</AnneeScolaireContext.Provider>;
}

export function useAnneeScolaire(): AnneeScolaireContextValue {
  const ctx = useContext(AnneeScolaireContext);
  if (!ctx) {
    throw new Error("useAnneeScolaire doit être utilisé dans AnneeScolaireProvider");
  }
  return ctx;
}
