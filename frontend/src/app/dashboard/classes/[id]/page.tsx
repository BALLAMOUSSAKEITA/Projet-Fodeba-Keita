"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { downloadListeClassePdf, getClasseEleves } from "@/lib/api/classes";
import { ApiError } from "@/lib/api/client";
import { getToken } from "@/lib/auth/session";
import type { ClasseElevesResponse } from "@/types/classe";

export default function ClasseDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<ClasseElevesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      setData(await getClasseEleves(token, id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Classe introuvable");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDownloadPdf() {
    const token = getToken();
    if (!token || !data) return;
    setDownloading(true);
    try {
      const filename = `liste_${data.classe.nom.replace(/\s+/g, "_")}.pdf`;
      await downloadListeClassePdf(token, id, filename);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur PDF");
    } finally {
      setDownloading(false);
    }
  }

  if (!data && !error) {
    return <p className="text-sm text-slate-500">Chargement...</p>;
  }

  if (error && !data) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>;
  }

  if (!data) return null;

  const { classe, effectif, capacite_max, eleves } = data;
  const depassement = effectif > capacite_max;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/dashboard/classes" className="text-sm text-emerald-700 hover:underline">
            ← Retour aux classes
          </Link>
          <h2 className="mt-2 text-2xl font-bold text-slate-900">{classe.nom}</h2>
          <p className="text-sm text-slate-500">
            Salle {classe.salle ?? "—"} · {effectif}/{capacite_max} élèves
            {depassement && (
              <span className="ml-2 rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                Capacité dépassée
              </span>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={handleDownloadPdf}
          disabled={downloading}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {downloading ? "Génération..." : "Télécharger liste PDF"}
        </button>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">N°</th>
              <th className="px-4 py-3 font-medium">Matricule</th>
              <th className="px-4 py-3 font-medium">Nom complet</th>
              <th className="px-4 py-3 font-medium">Sexe</th>
              <th className="px-4 py-3 font-medium">Naissance</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {eleves.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">Aucun élève affecté</td></tr>
            ) : (
              eleves.map((e, i) => (
                <tr key={e.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-500">{i + 1}</td>
                  <td className="px-4 py-3 font-mono text-xs">{e.matricule}</td>
                  <td className="px-4 py-3 font-medium">{e.prenoms} {e.nom}</td>
                  <td className="px-4 py-3">{e.sexe === "M" ? "G" : "F"}</td>
                  <td className="px-4 py-3">{e.date_naissance}</td>
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/eleves/${e.id}`} className="text-emerald-700 hover:underline">
                      Fiche
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
