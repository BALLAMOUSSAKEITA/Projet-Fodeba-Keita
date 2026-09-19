"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { createIncident, listIncidents } from "@/lib/api/presences";
import { getClasseEleves } from "@/lib/api/classes";
import { getAnneeActive, listClasses } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Incident } from "@/types/presences";
import type { Classe } from "@/types/parametrage";

const TYPE_LABELS: Record<string, string> = {
  avertissement: "Avertissement",
  blame: "Blâme",
  exclusion_temporaire: "Exclusion temporaire",
  convocation: "Convocation",
  autre: "Autre",
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function DisciplinePage() {
  const [classes, setClasses] = useState<Classe[]>([]);
  const [classeId, setClasseId] = useState("");
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [eleves, setEleves] = useState<{ id: string; nom: string; prenoms: string }[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    eleve_id: "",
    date: todayIso(),
    type: "avertissement",
    description: "",
    sanction: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canManage = hasPermission("attendance.manage");
  const canView = canManage || hasPermission("attendance.view");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId) return;
    try {
      setIncidents(await listIncidents(token, { classe_id: classeId }));
      const data = await getClasseEleves(token, classeId);
      setEleves(data.eleves.map((e) => ({ id: e.id, nom: e.nom, prenoms: e.prenoms })));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [classeId]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    getAnneeActive(token).then((annee) => {
      listClasses(token, annee.id).then((c) => {
        setClasses(c);
        if (c.length) setClasseId(c[0].id);
      });
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !canManage) return;
    setSaving(true);
    setError(null);
    try {
      await createIncident(token, {
        eleve_id: form.eleve_id,
        classe_id: classeId,
        date: form.date,
        type: form.type,
        description: form.description,
        sanction: form.sanction || undefined,
      });
      setShowForm(false);
      setForm({ eleve_id: "", date: todayIso(), type: "avertissement", description: "", sanction: "" });
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement");
    } finally {
      setSaving(false);
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Accès refusé.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/presences" className="text-sm text-emerald-700 hover:underline">
          ← Présences
        </Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Registre discipline</h2>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-3">
        <select
          value={classeId}
          onChange={(e) => setClasseId(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {classes.map((c) => (
            <option key={c.id} value={c.id}>{c.nom}</option>
          ))}
        </select>
        {canManage && (
          <button
            type="button"
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            {showForm ? "Annuler" : "Nouvel incident"}
          </button>
        )}
      </div>

      {showForm && canManage && (
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-medium text-slate-600">Élève</label>
              <select
                required
                value={form.eleve_id}
                onChange={(e) => setForm((f) => ({ ...f, eleve_id: e.target.value }))}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">— Sélectionner —</option>
                {eleves.map((el) => (
                  <option key={el.id} value={el.id}>{el.prenoms} {el.nom}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Date</label>
              <input
                type="date"
                required
                value={form.date}
                onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {Object.entries(TYPE_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Sanction</label>
              <input
                type="text"
                value={form.sanction}
                onChange={(e) => setForm((f) => ({ ...f, sanction: e.target.value }))}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder="Optionnel"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Description</label>
            <textarea
              required
              minLength={5}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={3}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
          >
            {saving ? "Enregistrement…" : "Enregistrer"}
          </button>
        </form>
      )}

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Élève</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-left">Description</th>
              <th className="px-4 py-3 text-left">Sanction</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc) => (
              <tr key={inc.id} className="border-t border-slate-100">
                <td className="px-4 py-2">{inc.date}</td>
                <td className="px-4 py-2">{inc.eleve_prenoms} {inc.eleve_nom}</td>
                <td className="px-4 py-2">{TYPE_LABELS[inc.type] ?? inc.type}</td>
                <td className="px-4 py-2 text-slate-600">{inc.description}</td>
                <td className="px-4 py-2">{inc.sanction ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {incidents.length === 0 && (
          <p className="px-4 py-6 text-sm text-slate-500">Aucun incident enregistré.</p>
        )}
      </div>
    </div>
  );
}
