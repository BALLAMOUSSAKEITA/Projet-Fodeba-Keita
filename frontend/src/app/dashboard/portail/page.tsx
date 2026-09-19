"use client";

import { useEffect, useState } from "react";
import { getResumeEnfant, listMesEnfants } from "@/lib/api/portail";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { EnfantItem, PortailResume } from "@/types/communication";

function fmt(n: string | number) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

export default function PortailPage() {
  const [enfants, setEnfants] = useState<EnfantItem[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [resume, setResume] = useState<PortailResume | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canAccess = hasPermission("parent.portal");

  useEffect(() => {
    const token = getToken();
    if (!token || !canAccess) return;
    listMesEnfants(token)
      .then((e) => {
        setEnfants(e);
        if (e.length) setSelectedId(e[0].eleve_id);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erreur"));
  }, [canAccess]);

  useEffect(() => {
    const token = getToken();
    if (!token || !selectedId) return;
    getResumeEnfant(token, selectedId)
      .then(setResume)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erreur"));
  }, [selectedId]);

  if (!canAccess) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Le portail parent est réservé aux comptes tuteurs.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Portail parent</h2>
        <p className="mt-1 text-sm text-slate-600">Notes, absences, solde et annonces de votre enfant</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {enfants.length > 1 && (
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {enfants.map((e) => (
            <option key={e.eleve_id} value={e.eleve_id}>
              {e.prenoms} {e.nom} ({e.matricule})
            </option>
          ))}
        </select>
      )}

      {resume && (
        <>
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6">
            <h3 className="text-lg font-bold text-emerald-900">
              {resume.prenoms} {resume.nom}
            </h3>
            <p className="text-sm text-emerald-800">
              {resume.matricule} · {resume.classe_nom ?? "—"} · {resume.annee_libelle}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Scolarité due</p>
              <p className="text-xl font-bold text-slate-900">{fmt(resume.total_du)}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-emerald-700">Payé</p>
              <p className="text-xl font-bold text-emerald-800">{fmt(resume.total_paye)}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-red-700">Reste à payer</p>
              <p className="text-xl font-bold text-red-800">{fmt(resume.total_restant)}</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Jours absents</p>
              <p className="text-2xl font-bold">{resume.jours_absents}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Non justifiées</p>
              <p className="text-2xl font-bold text-red-700">{resume.absences_non_justifiees}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Retards</p>
              <p className="text-2xl font-bold">{resume.jours_retards}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Incidents</p>
              <p className="text-2xl font-bold">{resume.incidents_count}</p>
            </div>
          </div>

          {resume.periodes_notes.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
              <h4 className="border-b border-slate-100 px-4 py-3 font-semibold text-slate-900">Notes par période</h4>
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-3 text-left">Période</th>
                    <th className="px-4 py-3 text-left">Moyenne</th>
                    <th className="px-4 py-3 text-left">Rang</th>
                  </tr>
                </thead>
                <tbody>
                  {resume.periodes_notes.map((p) => (
                    <tr key={p.periode_id} className="border-t border-slate-100">
                      <td className="px-4 py-2">{p.periode_libelle}</td>
                      <td className="px-4 py-2 font-medium">
                        {p.moyenne_generale != null ? Number(p.moyenne_generale).toFixed(2) : "—"}
                      </td>
                      <td className="px-4 py-2">{p.rang ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="space-y-3">
            <h4 className="font-semibold text-slate-900">Annonces de l&apos;école</h4>
            {resume.annonces.map((a) => (
              <div key={a.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="font-medium text-slate-900">{a.titre}</p>
                <p className="mt-1 text-sm text-slate-600 whitespace-pre-wrap">{a.contenu}</p>
                <p className="mt-2 text-xs text-slate-500">{a.date_publication}</p>
              </div>
            ))}
            {resume.annonces.length === 0 && (
              <p className="text-sm text-slate-500">Aucune annonce pour le moment.</p>
            )}
          </div>
        </>
      )}

      {enfants.length === 0 && !error && (
        <p className="text-sm text-slate-500">Aucun enfant lié à votre compte.</p>
      )}
    </div>
  );
}
