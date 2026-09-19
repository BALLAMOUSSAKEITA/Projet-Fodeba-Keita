"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  getAbsencesAJustifier,
  getAppel,
  getClasseRecap,
  reviewJustification,
  saveAppel,
} from "@/lib/api/presences";
import { getAnneeActive, listClasses } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { AppelPresence, ClasseRecap, PresenceEleveRow, StatutPresence } from "@/types/presences";
import type { Classe } from "@/types/parametrage";

type Tab = "appel" | "tableau" | "justifications";

const STATUT_LABELS: Record<StatutPresence, string> = {
  present: "Présent",
  absent: "Absent",
  retard: "Retard",
  excuse: "Excusé",
};

const STATUT_COLORS: Record<StatutPresence, string> = {
  present: "bg-emerald-100 text-emerald-800",
  absent: "bg-red-100 text-red-800",
  retard: "bg-amber-100 text-amber-800",
  excuse: "bg-blue-100 text-blue-800",
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function monthStartIso() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
}

export default function PresencesPage() {
  const [tab, setTab] = useState<Tab>("appel");
  const [classes, setClasses] = useState<Classe[]>([]);
  const [classeId, setClasseId] = useState("");
  const [appelDate, setAppelDate] = useState(todayIso());
  const [dateDebut, setDateDebut] = useState(monthStartIso());
  const [dateFin, setDateFin] = useState(todayIso());
  const [appel, setAppel] = useState<AppelPresence | null>(null);
  const [localStatuts, setLocalStatuts] = useState<Record<string, StatutPresence>>({});
  const [recap, setRecap] = useState<ClasseRecap | null>(null);
  const [pending, setPending] = useState<PresenceEleveRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canManage = hasPermission("attendance.manage");
  const canView = canManage || hasPermission("attendance.view");

  const loadAppel = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId || !appelDate) return;
    try {
      const data = await getAppel(token, classeId, appelDate);
      setAppel(data);
      const statuts: Record<string, StatutPresence> = {};
      for (const e of data.eleves) {
        statuts[e.eleve_id] = e.statut as StatutPresence;
      }
      setLocalStatuts(statuts);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [classeId, appelDate]);

  const loadRecap = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId) return;
    try {
      setRecap(await getClasseRecap(token, classeId, dateDebut, dateFin));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [classeId, dateDebut, dateFin]);

  const loadPending = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      setPending(await getAbsencesAJustifier(token, classeId || undefined));
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

  useEffect(() => {
    if (tab === "appel") loadAppel();
    if (tab === "tableau") loadRecap();
    if (tab === "justifications") loadPending();
  }, [tab, loadAppel, loadRecap, loadPending]);

  function setStatut(eleveId: string, statut: StatutPresence) {
    setLocalStatuts((s) => ({ ...s, [eleveId]: statut }));
  }

  async function handleSaveAppel() {
    const token = getToken();
    if (!token || !appel) return;
    setSaving(true);
    setError(null);
    try {
      const presences = appel.eleves.map((e) => ({
        eleve_id: e.eleve_id,
        statut: localStatuts[e.eleve_id] ?? "present",
        retard_minutes:
          localStatuts[e.eleve_id] === "retard" ? (e.retard_minutes ?? 15) : null,
        motif: localStatuts[e.eleve_id] === "absent" ? (e.motif ?? "Non précisé") : null,
      }));
      const updated = await saveAppel(token, classeId, appelDate, presences);
      setAppel(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement");
    } finally {
      setSaving(false);
    }
  }

  async function handleReview(presenceId: string, statut: "acceptee" | "refusee") {
    const token = getToken();
    if (!token) return;
    try {
      await reviewJustification(token, presenceId, statut);
      await loadPending();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès aux présences.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Présences & absences</h2>
          <p className="mt-1 text-sm text-slate-600">Appel journalier, cumuls et justifications</p>
        </div>
        <Link
          href="/dashboard/presences/discipline"
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Registre discipline →
        </Link>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(["appel", "tableau", "justifications"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "appel" ? "Appel" : t === "tableau" ? "Tableau de bord" : "Justifications"}
          </button>
        ))}
      </div>

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
        {tab === "appel" && (
          <input
            type="date"
            value={appelDate}
            onChange={(e) => setAppelDate(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        )}
        {tab === "tableau" && (
          <>
            <input
              type="date"
              value={dateDebut}
              onChange={(e) => setDateDebut(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              type="date"
              value={dateFin}
              onChange={(e) => setDateFin(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </>
        )}
        {tab === "appel" && canManage && (
          <button
            type="button"
            onClick={handleSaveAppel}
            disabled={saving || !appel}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
          >
            {saving ? "Enregistrement…" : "Enregistrer l'appel"}
          </button>
        )}
      </div>

      {tab === "appel" && appel && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Statut</th>
                {canManage && <th className="px-4 py-3 text-left">Actions rapides</th>}
              </tr>
            </thead>
            <tbody>
              {appel.eleves.map((e) => {
                const statut = (localStatuts[e.eleve_id] ?? "present") as StatutPresence;
                return (
                  <tr key={e.eleve_id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{e.prenoms} {e.nom}</td>
                    <td className="px-4 py-2">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUT_COLORS[statut]}`}>
                        {STATUT_LABELS[statut]}
                      </span>
                    </td>
                    {canManage && (
                      <td className="px-4 py-2">
                        <div className="flex gap-1">
                          {(["present", "absent", "retard"] as StatutPresence[]).map((s) => (
                            <button
                              key={s}
                              type="button"
                              onClick={() => setStatut(e.eleve_id, s)}
                              className={`rounded px-2 py-1 text-xs font-medium ${
                                statut === s
                                  ? "bg-emerald-700 text-white"
                                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                              }`}
                            >
                              {s === "present" ? "P" : s === "absent" ? "A" : "R"}
                            </button>
                          ))}
                        </div>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {tab === "tableau" && recap && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-4 py-3">
            <h3 className="font-semibold text-slate-900">
              {recap.classe_nom} — {recap.date_debut} → {recap.date_fin}
            </h3>
            <p className="text-xs text-slate-500">Effectif : {recap.effectif}</p>
          </div>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Absences</th>
                <th className="px-4 py-3 text-left">Retards</th>
                <th className="px-4 py-3 text-left">Min. retard</th>
                <th className="px-4 py-3 text-left">Excusés</th>
                <th className="px-4 py-3 text-left">Non justifiées</th>
              </tr>
            </thead>
            <tbody>
              {recap.eleves
                .filter((e) => e.jours_absents + e.jours_retards + e.jours_excuses > 0)
                .sort((a, b) => b.absences_non_justifiees - a.absences_non_justifiees)
                .map((e) => (
                  <tr key={e.eleve_id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{e.prenoms} {e.nom}</td>
                    <td className="px-4 py-2">{e.jours_absents}</td>
                    <td className="px-4 py-2">{e.jours_retards}</td>
                    <td className="px-4 py-2">{e.minutes_retard_total}</td>
                    <td className="px-4 py-2">{e.jours_excuses}</td>
                    <td className="px-4 py-2 font-semibold text-red-700">{e.absences_non_justifiees}</td>
                  </tr>
                ))}
            </tbody>
          </table>
          {recap.eleves.every((e) => e.jours_absents + e.jours_retards === 0) && (
            <p className="px-4 py-6 text-sm text-slate-500">Aucune absence sur la période.</p>
          )}
        </div>
      )}

      {tab === "justifications" && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Statut</th>
                <th className="px-4 py-3 text-left">Motif</th>
                <th className="px-4 py-3 text-left">Justification</th>
                {canManage && <th className="px-4 py-3 text-left">Décision</th>}
              </tr>
            </thead>
            <tbody>
              {pending.map((p) => (
                <tr key={p.presence_id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{p.prenoms} {p.nom}</td>
                  <td className="px-4 py-2">{STATUT_LABELS[p.statut as StatutPresence] ?? p.statut}</td>
                  <td className="px-4 py-2 text-slate-600">{p.motif ?? "—"}</td>
                  <td className="px-4 py-2 text-slate-600">{p.justification ?? "—"}</td>
                  {canManage && p.presence_id && (
                    <td className="px-4 py-2">
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => handleReview(p.presence_id!, "acceptee")}
                          className="text-emerald-700 hover:underline"
                        >
                          Accepter
                        </button>
                        <button
                          type="button"
                          onClick={() => handleReview(p.presence_id!, "refusee")}
                          className="text-red-700 hover:underline"
                        >
                          Refuser
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {pending.length === 0 && (
            <p className="px-4 py-6 text-sm text-slate-500">Aucune justification en attente.</p>
          )}
        </div>
      )}
    </div>
  );
}
