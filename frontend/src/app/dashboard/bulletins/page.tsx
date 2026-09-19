"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  createDecisionPassage,
  downloadBulletinAnnuelPdf,
  downloadBulletinElevePdf,
  downloadBulletinsClassePdf,
  getPalmares,
  getStatsPedagogiques,
} from "@/lib/api/bulletins";
import { getMoyennesClasse } from "@/lib/api/notes";
import { getAnneeActive, listClasses, listPeriodes } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Palmares, StatsPedagogiques } from "@/types/bulletins";
import type { MoyennesClasse } from "@/types/notes";
import type { AnneeScolaire, Classe, Periode } from "@/types/parametrage";

const DECISION_LABELS: Record<string, string> = {
  admis: "Admis",
  redouble: "Redouble",
  exclu: "Exclu",
};

export default function BulletinsPage() {
  const [classes, setClasses] = useState<Classe[]>([]);
  const [periodes, setPeriodes] = useState<Periode[]>([]);
  const [annee, setAnnee] = useState<AnneeScolaire | null>(null);
  const [classeId, setClasseId] = useState("");
  const [periodeId, setPeriodeId] = useState("");
  const [stats, setStats] = useState<StatsPedagogiques | null>(null);
  const [palmares, setPalmares] = useState<Palmares | null>(null);
  const [moyennes, setMoyennes] = useState<MoyennesClasse | null>(null);
  const [decisions, setDecisions] = useState<Record<string, string>>({});
  const [observations, setObservations] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const canValidate = hasPermission("grades.validate_bulletins");
  const canView = canValidate || hasPermission("grades.modify");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !classeId || !periodeId) return;
    setLoading(true);
    setError(null);
    try {
      const [s, p, m] = await Promise.all([
        getStatsPedagogiques(token, classeId, periodeId),
        getPalmares(token, classeId, periodeId),
        getMoyennesClasse(token, classeId, periodeId),
      ]);
      setStats(s);
      setPalmares(p);
      setMoyennes(m);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [classeId, periodeId]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    getAnneeActive(token).then((a) => {
      setAnnee(a);
      Promise.all([listClasses(token, a.id), listPeriodes(token, a.id)]).then(([c, p]) => {
        const primaire = c.filter((cl) => cl.niveau?.type !== "maternelle");
        setClasses(primaire.length ? primaire : c);
        setPeriodes(p);
        if (primaire.length) setClasseId(primaire[0].id);
        else if (c.length) setClasseId(c[0].id);
        if (p.length) setPeriodeId(p[0].id);
      });
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleDownloadClasse() {
    const token = getToken();
    if (!token || !classeId || !periodeId) return;
    setDownloading(true);
    try {
      const nom = classes.find((c) => c.id === classeId)?.nom ?? "classe";
      await downloadBulletinsClassePdf(
        token,
        classeId,
        periodeId,
        `bulletins_${nom.replace(/\s+/g, "_")}.pdf`,
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur téléchargement");
    } finally {
      setDownloading(false);
    }
  }

  async function handleDownloadEleve(eleveId: string, matricule: string, annuel = false) {
    const token = getToken();
    if (!token || !periodeId) return;
    try {
      if (annuel) {
        await downloadBulletinAnnuelPdf(token, eleveId, `bulletin_annuel_${matricule}.pdf`);
      } else {
        await downloadBulletinElevePdf(
          token,
          eleveId,
          periodeId,
          `bulletin_${matricule}.pdf`,
        );
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur téléchargement");
    }
  }

  async function handleSaveDecision(eleveId: string) {
    const token = getToken();
    const decision = decisions[eleveId];
    if (!token || !decision) return;
    try {
      await createDecisionPassage(token, {
        eleve_id: eleveId,
        decision,
        observation: observations[eleveId] || null,
        annee_scolaire_id: annee?.id,
      });
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès aux bulletins.
      </div>
    );
  }

  const eleves = moyennes?.eleves ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Bulletins scolaires</h2>
          <p className="mt-1 text-sm text-slate-600">
            Génération PDF, statistiques, palmarès et décisions de passage
          </p>
        </div>
        <Link
          href="/dashboard/bulletins/maternelle"
          className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-800 hover:bg-emerald-100"
        >
          Maternelle →
        </Link>
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
        <select
          value={periodeId}
          onChange={(e) => setPeriodeId(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {periodes.map((p) => (
            <option key={p.id} value={p.id}>{p.libelle}</option>
          ))}
        </select>
        <button
          type="button"
          onClick={handleDownloadClasse}
          disabled={downloading || !classeId}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {downloading ? "Génération…" : "Télécharger bulletins (classe)"}
        </button>
      </div>

      {loading && <p className="text-sm text-slate-500">Chargement…</p>}

      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Effectif" value={String(stats.effectif)} />
          <StatCard label="Moyenne classe" value={stats.moyenne_classe?.toFixed(2) ?? "—"} />
          <StatCard
            label="Taux de réussite"
            value={stats.taux_reussite != null ? `${stats.taux_reussite}%` : "—"}
          />
          <StatCard label="Meilleur élève" value={stats.meilleur_eleve ?? "—"} />
        </div>
      )}

      {palmares && palmares.items.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-4 py-3">
            <h3 className="font-semibold text-slate-900">Palmarès — {palmares.periode_libelle}</h3>
          </div>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Rang</th>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Moyenne</th>
                <th className="px-4 py-3 text-left">Appréciation</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {palmares.items.map((item) => (
                <tr key={item.eleve_id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-bold text-emerald-700">{item.rang}</td>
                  <td className="px-4 py-2">{item.prenoms} {item.nom}</td>
                  <td className="px-4 py-2 font-semibold">{item.moyenne_generale}</td>
                  <td className="px-4 py-2 text-slate-600">{item.appreciation ?? "—"}</td>
                  <td className="px-4 py-2">
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => handleDownloadEleve(item.eleve_id, item.matricule)}
                        className="text-emerald-700 hover:underline"
                      >
                        Bulletin
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDownloadEleve(item.eleve_id, item.matricule, true)}
                        className="text-slate-600 hover:underline"
                      >
                        Annuel
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {canValidate && eleves.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-4 py-3">
            <h3 className="font-semibold text-slate-900">Décisions de passage</h3>
            <p className="text-xs text-slate-500">Année {annee?.libelle ?? "—"}</p>
          </div>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Moyenne</th>
                <th className="px-4 py-3 text-left">Décision</th>
                <th className="px-4 py-3 text-left">Observation</th>
                <th className="px-4 py-3 text-left" />
              </tr>
            </thead>
            <tbody>
              {eleves.map((e) => (
                <tr key={e.eleve_id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{e.prenoms} {e.nom}</td>
                  <td className="px-4 py-2">{e.moyenne_generale ?? "—"}</td>
                  <td className="px-4 py-2">
                    <select
                      value={decisions[e.eleve_id] ?? ""}
                      onChange={(ev) =>
                        setDecisions((d) => ({ ...d, [e.eleve_id]: ev.target.value }))
                      }
                      className="rounded border border-slate-300 px-2 py-1 text-sm"
                    >
                      <option value="">—</option>
                      {Object.entries(DECISION_LABELS).map(([val, label]) => (
                        <option key={val} value={val}>{label}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-2">
                    <input
                      type="text"
                      value={observations[e.eleve_id] ?? ""}
                      onChange={(ev) =>
                        setObservations((o) => ({ ...o, [e.eleve_id]: ev.target.value }))
                      }
                      placeholder="Optionnel"
                      className="w-full min-w-[120px] rounded border border-slate-300 px-2 py-1 text-sm"
                    />
                  </td>
                  <td className="px-4 py-2">
                    <button
                      type="button"
                      disabled={!decisions[e.eleve_id]}
                      onClick={() => handleSaveDecision(e.eleve_id)}
                      className="rounded bg-slate-800 px-3 py-1 text-xs font-medium text-white hover:bg-slate-900 disabled:opacity-40"
                    >
                      Enregistrer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}
