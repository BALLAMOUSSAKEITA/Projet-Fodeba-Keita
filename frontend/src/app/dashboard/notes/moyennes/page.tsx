"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getMoyennesClasse, validerNotes } from "@/lib/api/notes";
import { getAnneeActive, listClasses, listPeriodes } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { MoyennesClasse } from "@/types/notes";
import type { Classe, Periode } from "@/types/parametrage";

export default function MoyennesPage() {
  const [classes, setClasses] = useState<Classe[]>([]);
  const [periodes, setPeriodes] = useState<Periode[]>([]);
  const [classeId, setClasseId] = useState("");
  const [periodeId, setPeriodeId] = useState("");
  const [data, setData] = useState<MoyennesClasse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const canValidate = hasPermission("grades.validate_bulletins");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId || !periodeId) return;
    try {
      setData(await getMoyennesClasse(token, classeId, periodeId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [classeId, periodeId]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    getAnneeActive(token).then((annee) => {
      Promise.all([listClasses(token), listPeriodes(token, annee.id)]).then(([c, p]) => {
        setClasses(c);
        setPeriodes(p);
        if (c.length) setClasseId(c[0].id);
        if (p.length) setPeriodeId(p[0].id);
      });
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleValider() {
    const token = getToken();
    if (!token) return;
    try {
      await validerNotes(token, classeId, periodeId);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }

  const ranked = data?.eleves.filter((e) => e.rang != null).sort((a, b) => (a.rang ?? 99) - (b.rang ?? 99)) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/notes" className="text-sm text-emerald-700 hover:underline">← Saisie notes</Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Moyennes & rangs</h2>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-3">
        <select value={classeId} onChange={(e) => setClasseId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
        </select>
        <select value={periodeId} onChange={(e) => setPeriodeId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {periodes.map((p) => <option key={p.id} value={p.id}>{p.libelle}</option>)}
        </select>
        {canValidate && data && !data.verrouille && (
          <button
            type="button"
            onClick={handleValider}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            Valider & verrouiller
          </button>
        )}
        {data?.verrouille && (
          <span className="rounded-lg bg-amber-100 px-3 py-2 text-sm font-medium text-amber-800">
            Période verrouillée
          </span>
        )}
      </div>

      {data && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Rang</th>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Moy. générale</th>
                <th className="px-4 py-3 text-left">Appréciation</th>
                {data.eleves[0]?.moyennes_matieres.map((m) => (
                  <th key={m.matiere_id} className="px-4 py-3 text-left">{m.matiere_code}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ranked.map((e) => (
                <tr key={e.eleve_id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-bold text-emerald-700">{e.rang ?? "—"}</td>
                  <td className="px-4 py-2">{e.prenoms} {e.nom}</td>
                  <td className="px-4 py-2 font-semibold">{e.moyenne_generale ?? "—"}</td>
                  <td className="px-4 py-2 text-slate-600">{e.appreciation_generale ?? "—"}</td>
                  {e.moyennes_matieres.map((m) => (
                    <td key={m.matiere_id} className="px-4 py-2">{m.moyenne ?? "—"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
