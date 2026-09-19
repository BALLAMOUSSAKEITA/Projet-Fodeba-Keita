"use client";

import { KeyboardEvent, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  createEvaluation,
  getGrilleNotes,
  listEvaluations,
  listTypesEvaluation,
  saveNotes,
} from "@/lib/api/notes";
import { getAnneeActive, listClasses, listMatieres, listPeriodes } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Evaluation, GrilleNotes, TypeEvaluation } from "@/types/notes";
import type { Classe, Matiere, Periode } from "@/types/parametrage";

export default function NotesPage() {
  const [classes, setClasses] = useState<Classe[]>([]);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [periodes, setPeriodes] = useState<Periode[]>([]);
  const [types, setTypes] = useState<TypeEvaluation[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [classeId, setClasseId] = useState("");
  const [matiereId, setMatiereId] = useState("");
  const [periodeId, setPeriodeId] = useState("");
  const [evaluationId, setEvaluationId] = useState("");
  const [grille, setGrille] = useState<GrilleNotes | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const canModify = hasPermission("grades.modify");

  const loadRefs = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    const annee = await getAnneeActive(token);
    const [c, m, p, t] = await Promise.all([
      listClasses(token),
      listMatieres(token),
      listPeriodes(token, annee.id),
      listTypesEvaluation(token),
    ]);
    setClasses(c);
    setMatieres(m);
    setPeriodes(p);
    setTypes(t);
    if (c.length) setClasseId(c[0].id);
    if (m.length) setMatiereId(m[0].id);
    if (p.length) setPeriodeId(p[0].id);
  }, []);

  const loadEvaluations = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId || !matiereId || !periodeId) return;
    const evs = await listEvaluations(token, { classe_id: classeId, matiere_id: matiereId, periode_id: periodeId });
    setEvaluations(evs);
    if (evs.length) setEvaluationId(evs[0].id);
    else setEvaluationId("");
  }, [classeId, matiereId, periodeId]);

  const loadGrille = useCallback(async () => {
    const token = getToken();
    if (!token || !evaluationId) {
      setGrille(null);
      return;
    }
    try {
      const data = await getGrilleNotes(token, evaluationId);
      setGrille(data);
      const init: Record<string, string> = {};
      data.eleves.forEach((e) => {
        if (e.note?.is_absent) init[e.eleve_id] = "ABS";
        else if (e.note?.valeur != null) init[e.eleve_id] = String(e.note.valeur);
        else init[e.eleve_id] = "";
      });
      setValues(init);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [evaluationId]);

  useEffect(() => { loadRefs(); }, [loadRefs]);
  useEffect(() => { loadEvaluations(); }, [loadEvaluations]);
  useEffect(() => { loadGrille(); }, [loadGrille]);

  async function handleCreateEvaluation() {
    const token = getToken();
    if (!token || !types[0]) return;
    const ev = await createEvaluation(token, {
      libelle: `Évaluation ${evaluations.length + 1}`,
      classe_id: classeId,
      matiere_id: matiereId,
      periode_id: periodeId,
      type_evaluation_id: types[0].id,
    });
    setEvaluationId(ev.id);
    await loadEvaluations();
  }

  async function handleSave() {
    const token = getToken();
    if (!token || !evaluationId || !grille) return;
    setSaving(true);
    setError(null);
    try {
      const notes = grille.eleves.map((e) => {
        const v = values[e.eleve_id]?.trim().toUpperCase();
        if (v === "ABS" || v === "") {
          return { eleve_id: e.eleve_id, is_absent: v === "ABS", valeur: null };
        }
        return { eleve_id: e.eleve_id, valeur: parseFloat(v), is_absent: false };
      });
      await saveNotes(token, evaluationId, notes);
      await loadGrille();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de sauvegarde");
    } finally {
      setSaving(false);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>, index: number) {
    if (e.key === "Enter" || (e.key === "Tab" && !e.shiftKey)) {
      e.preventDefault();
      const next = inputRefs.current[index + 1];
      if (next) next.focus();
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Saisie des notes</h2>
          <p className="text-sm text-slate-500">Tab / Entrée pour naviguer · ABS pour absent</p>
        </div>
        <Link href="/dashboard/notes/moyennes" className="text-sm text-emerald-700 hover:underline">
          Voir moyennes & rangs →
        </Link>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-3">
        <select value={classeId} onChange={(e) => setClasseId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
        </select>
        <select value={matiereId} onChange={(e) => setMatiereId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {matieres.map((m) => <option key={m.id} value={m.id}>{m.libelle}</option>)}
        </select>
        <select value={periodeId} onChange={(e) => setPeriodeId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {periodes.map((p) => <option key={p.id} value={p.id}>{p.libelle}</option>)}
        </select>
        <select value={evaluationId} onChange={(e) => setEvaluationId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {evaluations.length === 0 ? <option value="">— Aucune évaluation —</option> : null}
          {evaluations.map((ev) => <option key={ev.id} value={ev.id}>{ev.libelle}</option>)}
        </select>
        {canModify && (
          <button type="button" onClick={handleCreateEvaluation} className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">
            + Nouvelle évaluation
          </button>
        )}
      </div>

      {grille?.verrouille && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Notes verrouillées pour cette période — saisie impossible
        </div>
      )}

      {grille && (
        <>
          <p className="text-sm text-slate-600">
            {grille.evaluation.libelle} · Barème {grille.echelle} (max {grille.bareme_max})
          </p>
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left">
                <tr>
                  <th className="px-4 py-3">Matricule</th>
                  <th className="px-4 py-3">Élève</th>
                  <th className="px-4 py-3">Note</th>
                  <th className="px-4 py-3">Appréciation</th>
                </tr>
              </thead>
              <tbody>
                {grille.eleves.map((e, i) => (
                  <tr key={e.eleve_id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-mono text-xs">{e.matricule}</td>
                    <td className="px-4 py-2">{e.prenoms} {e.nom}</td>
                    <td className="px-4 py-2">
                      <input
                        ref={(el) => { inputRefs.current[i] = el; }}
                        type="text"
                        value={values[e.eleve_id] ?? ""}
                        disabled={grille.verrouille || !canModify}
                        onChange={(ev) => setValues({ ...values, [e.eleve_id]: ev.target.value })}
                        onKeyDown={(ev) => handleKeyDown(ev, i)}
                        className="w-20 rounded border border-slate-300 px-2 py-1 text-center font-mono"
                        placeholder="—"
                      />
                    </td>
                    <td className="px-4 py-2 text-slate-600">
                      {e.note?.appreciation_auto ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {canModify && !grille.verrouille && (
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="rounded-lg bg-emerald-700 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              {saving ? "Enregistrement..." : "Enregistrer les notes"}
            </button>
          )}
        </>
      )}
    </div>
  );
}
