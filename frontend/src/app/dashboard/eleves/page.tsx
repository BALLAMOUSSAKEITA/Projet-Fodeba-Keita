"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { listEleves } from "@/lib/api/eleves";
import { listNiveaux } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { EleveListItem } from "@/types/eleve";
import type { Niveau } from "@/types/parametrage";

export default function ElevesPage() {
  const [eleves, setEleves] = useState<EleveListItem[]>([]);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [sexe, setSexe] = useState("");
  const [niveauId, setNiveauId] = useState("");
  const [statut, setStatut] = useState("actif");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const canEnroll = hasPermission("students.enroll");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    try {
      const [data, niveauxData] = await Promise.all([
        listEleves(token, {
          search: search || undefined,
          sexe: sexe || undefined,
          niveau_id: niveauId || undefined,
          statut: statut || undefined,
        }),
        listNiveaux(token),
      ]);
      setEleves(data.items);
      setTotal(data.total);
      setNiveaux(niveauxData);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [search, sexe, niveauId, statut]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Élèves</h2>
          <p className="text-sm text-slate-500">{total} élève(s) inscrit(s)</p>
        </div>
        {canEnroll && (
          <div className="flex flex-wrap gap-2">
            <Link
              href="/dashboard/eleves/nouveau"
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
            >
              + Inscrire un élève
            </Link>
            <Link
              href="/dashboard/eleves/transfert-entrant"
              className="rounded-lg border border-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50"
            >
              Transfert entrant
            </Link>
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="flex flex-wrap gap-3">
        <input
          placeholder="Rechercher (nom, prénom, matricule)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-[220px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <select
          value={sexe}
          onChange={(e) => setSexe(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Tous les sexes</option>
          <option value="M">Garçon</option>
          <option value="F">Fille</option>
        </select>
        <select
          value={niveauId}
          onChange={(e) => setNiveauId(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Tous les niveaux</option>
          {niveaux.map((n) => (
            <option key={n.id} value={n.id}>{n.libelle}</option>
          ))}
        </select>
        <select
          value={statut}
          onChange={(e) => setStatut(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="actif">Actifs</option>
          <option value="inactif">Inactifs</option>
          <option value="">Tous</option>
        </select>
        <button
          type="button"
          onClick={load}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
        >
          Filtrer
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Matricule</th>
              <th className="px-4 py-3 font-medium">Nom complet</th>
              <th className="px-4 py-3 font-medium">Sexe</th>
              <th className="px-4 py-3 font-medium">Niveau</th>
              <th className="px-4 py-3 font-medium">Classe</th>
              <th className="px-4 py-3 font-medium">Naissance</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-500">Chargement...</td></tr>
            ) : eleves.length === 0 ? (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-500">Aucun élève trouvé</td></tr>
            ) : (
              eleves.map((e) => (
                <tr key={e.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs">{e.matricule}</td>
                  <td className="px-4 py-3 font-medium">{e.prenoms} {e.nom}</td>
                  <td className="px-4 py-3">{e.sexe === "M" ? "Garçon" : "Fille"}</td>
                  <td className="px-4 py-3">{e.niveau_libelle ?? "—"}</td>
                  <td className="px-4 py-3">{e.classe_nom ?? "—"}</td>
                  <td className="px-4 py-3">{e.date_naissance}</td>
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/eleves/${e.id}`} className="text-emerald-700 hover:underline">
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
