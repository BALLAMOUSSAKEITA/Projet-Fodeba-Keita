"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  downloadBulletinMaternellePdf,
  getGrilleCompetences,
  saveGrilleCompetences,
} from "@/lib/api/bulletins";
import { getAnneeActive, listClasses, listPeriodes } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { CompetenceGrille, StatutCompetence } from "@/types/bulletins";
import type { Classe, Periode } from "@/types/parametrage";

const STATUT_OPTIONS: { value: StatutCompetence; label: string }[] = [
  { value: "", label: "—" },
  { value: "acquis", label: "Acquis" },
  { value: "en_cours", label: "En cours" },
  { value: "non_acquis", label: "Non acquis" },
];

export default function MaternellePage() {
  const [classes, setClasses] = useState<Classe[]>([]);
  const [periodes, setPeriodes] = useState<Periode[]>([]);
  const [classeId, setClasseId] = useState("");
  const [periodeId, setPeriodeId] = useState("");
  const [grille, setGrille] = useState<CompetenceGrille | null>(null);
  const [localEvals, setLocalEvals] = useState<Record<string, Record<string, StatutCompetence>>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const canEdit = hasPermission("grades.modify");
  const canView = canEdit || hasPermission("grades.validate_bulletins");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId || !periodeId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getGrilleCompetences(token, classeId, periodeId);
      setGrille(data);
      const evals: Record<string, Record<string, StatutCompetence>> = {};
      for (const eleve of data.eleves) {
        evals[eleve.eleve_id] = {};
        for (const comp of data.competences) {
          const statut = eleve.evaluations[comp.id];
          evals[eleve.eleve_id][comp.id] = (statut as StatutCompetence) ?? "";
        }
      }
      setLocalEvals(evals);
    } catch (err) {
      setGrille(null);
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [classeId, periodeId]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    getAnneeActive(token).then((annee) => {
      Promise.all([listClasses(token, annee.id), listPeriodes(token, annee.id)]).then(([c, p]) => {
        const maternelle = c.filter((cl) => cl.niveau?.type === "maternelle");
        setClasses(maternelle);
        setPeriodes(p);
        if (maternelle.length) setClasseId(maternelle[0].id);
        if (p.length) setPeriodeId(p[0].id);
      });
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  function setStatut(eleveId: string, competenceId: string, statut: StatutCompetence) {
    setLocalEvals((prev) => ({
      ...prev,
      [eleveId]: { ...prev[eleveId], [competenceId]: statut },
    }));
  }

  async function handleSave() {
    const token = getToken();
    if (!token || !grille) return;
    setSaving(true);
    setError(null);
    try {
      const items = grille.eleves.map((eleve) => ({
        eleve_id: eleve.eleve_id,
        evaluations: grille.competences
          .map((comp) => ({
            competence_id: comp.id,
            statut: localEvals[eleve.eleve_id]?.[comp.id] ?? "",
          }))
          .filter((e) => e.statut !== "")
          .map((e) => ({ competence_id: e.competence_id, statut: e.statut })),
      }));
      const updated = await saveGrilleCompetences(token, classeId, periodeId, items);
      setGrille(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement");
    } finally {
      setSaving(false);
    }
  }

  async function handleDownload(eleveId: string, matricule: string) {
    const token = getToken();
    if (!token || !periodeId) return;
    try {
      await downloadBulletinMaternellePdf(
        token,
        eleveId,
        periodeId,
        `bulletin_maternelle_${matricule}.pdf`,
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur téléchargement");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès aux évaluations maternelle.
      </div>
    );
  }

  const competencesByDomaine = grille?.competences.reduce<Record<string, typeof grille.competences>>(
    (acc, comp) => {
      if (!acc[comp.domaine]) acc[comp.domaine] = [];
      acc[comp.domaine].push(comp);
      return acc;
    },
    {},
  ) ?? {};

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/bulletins" className="text-sm text-emerald-700 hover:underline">
          ← Bulletins primaire
        </Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Évaluation maternelle</h2>
        <p className="mt-1 text-sm text-slate-600">Grille de compétences par domaine</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {classes.length === 0 ? (
        <div className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-600">
          Aucune classe maternelle configurée.
        </div>
      ) : (
        <>
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
            <select
              value={periodeId}
              onChange={(e) => setPeriodeId(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {periodes.map((p) => (
                <option key={p.id} value={p.id}>{p.libelle}</option>
              ))}
            </select>
            {canEdit && grille && (
              <button
                type="button"
                onClick={handleSave}
                disabled={saving}
                className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
              >
                {saving ? "Enregistrement…" : "Enregistrer"}
              </button>
            )}
          </div>

          {loading && <p className="text-sm text-slate-500">Chargement…</p>}

          {grille && grille.competences.length > 0 && (
            <div className="space-y-6">
              {Object.entries(competencesByDomaine).map(([domaine, comps]) => (
                <div
                  key={domaine}
                  className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm"
                >
                  <div className="border-b border-slate-100 bg-emerald-50 px-4 py-2">
                    <h3 className="font-semibold text-emerald-900">{domaine}</h3>
                  </div>
                  <table className="min-w-full text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="sticky left-0 z-10 bg-slate-50 px-4 py-3 text-left">Élève</th>
                        {comps.map((comp) => (
                          <th
                            key={comp.id}
                            className="min-w-[100px] px-2 py-3 text-left text-xs font-medium"
                            title={comp.libelle}
                          >
                            {comp.code}
                          </th>
                        ))}
                        <th className="px-4 py-3 text-left">PDF</th>
                      </tr>
                    </thead>
                    <tbody>
                      {grille.eleves.map((eleve) => (
                        <tr key={eleve.eleve_id} className="border-t border-slate-100">
                          <td className="sticky left-0 z-10 bg-white px-4 py-2 whitespace-nowrap">
                            {eleve.prenoms} {eleve.nom}
                          </td>
                          {comps.map((comp) => (
                            <td key={comp.id} className="px-2 py-2">
                              <select
                                value={localEvals[eleve.eleve_id]?.[comp.id] ?? ""}
                                onChange={(e) =>
                                  setStatut(
                                    eleve.eleve_id,
                                    comp.id,
                                    e.target.value as StatutCompetence,
                                  )
                                }
                                disabled={!canEdit}
                                className="w-full rounded border border-slate-300 px-1 py-1 text-xs disabled:bg-slate-50"
                              >
                                {STATUT_OPTIONS.map((opt) => (
                                  <option key={opt.value || "empty"} value={opt.value}>
                                    {opt.label}
                                  </option>
                                ))}
                              </select>
                            </td>
                          ))}
                          <td className="px-4 py-2">
                            <button
                              type="button"
                              onClick={() => handleDownload(eleve.eleve_id, eleve.matricule)}
                              className="text-emerald-700 hover:underline"
                            >
                              Bulletin
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}

          {grille && grille.competences.length === 0 && !loading && (
            <p className="text-sm text-slate-500">
              Aucune compétence définie pour ce niveau. Vérifiez le seed maternelle.
            </p>
          )}
        </>
      )}
    </div>
  );
}
