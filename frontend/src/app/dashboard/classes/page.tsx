"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { listClasseEffectifs } from "@/lib/api/classes";
import { getStatsEffectifs } from "@/lib/api/eleves";
import { ApiError } from "@/lib/api/client";
import { getToken } from "@/lib/auth/session";
import type { ClasseEffectif, EffectifStats } from "@/types/classe";

export default function ClassesPage() {
  const [classes, setClasses] = useState<ClasseEffectif[]>([]);
  const [stats, setStats] = useState<EffectifStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    try {
      const [effectifs, effectifStats] = await Promise.all([
        listClasseEffectifs(token),
        getStatsEffectifs(token),
      ]);
      setClasses(effectifs);
      setStats(effectifStats);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Classes</h2>
        <p className="text-sm text-slate-500">Effectifs par classe — année scolaire active</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total élèves" value={stats.total_eleves} />
          <StatCard label="Garçons" value={stats.total_garcons} />
          <StatCard label="Filles" value={stats.total_filles} />
          <StatCard label="Sans classe" value={stats.sans_classe} highlight={stats.sans_classe > 0} />
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Classe</th>
              <th className="px-4 py-3 font-medium">Niveau</th>
              <th className="px-4 py-3 font-medium">Salle</th>
              <th className="px-4 py-3 font-medium">Effectif</th>
              <th className="px-4 py-3 font-medium">Capacité</th>
              <th className="px-4 py-3 font-medium">Places restantes</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-500">Chargement...</td></tr>
            ) : classes.length === 0 ? (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-500">Aucune classe</td></tr>
            ) : (
              classes.map((c) => (
                <tr key={c.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{c.nom}</td>
                  <td className="px-4 py-3">{c.niveau_libelle}</td>
                  <td className="px-4 py-3">{c.salle ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={c.depassement ? "font-semibold text-red-600" : ""}>
                      {c.effectif}
                    </span>
                  </td>
                  <td className="px-4 py-3">{c.capacite_max}</td>
                  <td className="px-4 py-3">
                    {c.depassement ? (
                      <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                        Dépassement
                      </span>
                    ) : (
                      c.places_restantes
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/classes/${c.id}`} className="text-emerald-700 hover:underline">
                      Voir
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <div className={`rounded-xl border p-4 ${highlight ? "border-amber-200 bg-amber-50" : "border-slate-200 bg-white"}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}
