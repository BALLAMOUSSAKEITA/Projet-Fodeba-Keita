"use client";

import { useCallback, useEffect, useState } from "react";
import { BarChart } from "@/components/charts/BarChart";
import {
  downloadRapportCsv,
  downloadRapportExcel,
  downloadRapportPdf,
  getGraphiques,
  getRapportEffectifs,
  getRapportFinancier,
  getRapportPedagogique,
  getRapportPresence,
  getStatistiquesAnnuelles,
} from "@/lib/api/rapports";
import { getAnneeActive } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type {
  Graphiques,
  RapportEffectifs,
  RapportFinancier,
  RapportPedagogique,
  RapportPresence,
  StatistiquesAnnuelles,
} from "@/types/rapports";

type Tab = "effectifs" | "financier" | "pedagogique" | "presence" | "annuel";

function fmt(n: number | string) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

function yearStart() {
  return `${new Date().getFullYear()}-01-01`;
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function RapportsPage() {
  const [tab, setTab] = useState<Tab>("effectifs");
  const [graphiques, setGraphiques] = useState<Graphiques | null>(null);
  const [effectifs, setEffectifs] = useState<RapportEffectifs | null>(null);
  const [financier, setFinancier] = useState<RapportFinancier | null>(null);
  const [pedagogique, setPedagogique] = useState<RapportPedagogique | null>(null);
  const [presence, setPresence] = useState<RapportPresence | null>(null);
  const [annuel, setAnnuel] = useState<StatistiquesAnnuelles | null>(null);
  const [dateDebut, setDateDebut] = useState(yearStart());
  const [dateFin, setDateFin] = useState(todayIso());
  const [anneeId, setAnneeId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const canView = hasPermission("reports.view") || hasPermission("reports.view_pedagogical");

  useEffect(() => {
    const token = getToken();
    if (!token || !canView) return;
    getAnneeActive(token).then((a) => {
      setAnneeId(a.id);
      setDateDebut(a.date_debut);
    });
    getGraphiques(token).then(setGraphiques).catch(() => {});
  }, [canView]);

  const loadTab = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setError(null);
    try {
      if (tab === "effectifs") setEffectifs(await getRapportEffectifs(token));
      if (tab === "financier" && anneeId) {
        setFinancier(await getRapportFinancier(token, dateDebut, dateFin, anneeId));
      }
      if (tab === "pedagogique") setPedagogique(await getRapportPedagogique(token));
      if (tab === "presence") setPresence(await getRapportPresence(token, dateDebut, dateFin));
      if (tab === "annuel") setAnnuel(await getStatistiquesAnnuelles(token));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur chargement");
    }
  }, [tab, dateDebut, dateFin, anneeId]);

  useEffect(() => {
    loadTab();
  }, [loadTab]);

  async function handleExport(format: "csv" | "excel" | "pdf") {
    const token = getToken();
    if (!token) return;
    try {
      const dates = { debut: dateDebut, fin: dateFin, anneeId };
      if (format === "csv") {
        if (tab === "effectifs") await downloadRapportCsv(token, "effectifs");
        else if (tab === "financier") await downloadRapportCsv(token, "financier", dates);
      } else if (format === "excel") {
        const t = tab === "annuel" ? "annuel" : tab === "pedagogique" ? "pedagogique" : tab === "financier" ? "financier" : "effectifs";
        await downloadRapportExcel(token, t, tab === "financier" ? dates : undefined);
      } else {
        const t = tab === "annuel" ? "annuel" : tab === "financier" ? "financier" : "effectifs";
        await downloadRapportPdf(token, t, tab === "financier" ? dates : undefined);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur export");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès aux rapports.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Rapports</h2>
          <p className="mt-1 text-sm text-slate-600">Effectifs, finances, pédagogie et statistiques annuelles</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => handleExport("csv")} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">CSV</button>
          <button type="button" onClick={() => handleExport("excel")} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">Excel</button>
          <button type="button" onClick={() => handleExport("pdf")} className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800">PDF</button>
        </div>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {graphiques && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 font-semibold text-slate-900">Effectifs par niveau</h3>
            <BarChart labels={graphiques.effectifs_par_niveau.labels} values={graphiques.effectifs_par_niveau.values} />
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 font-semibold text-slate-900">Recettes par mois</h3>
            <BarChart
              labels={graphiques.recettes_par_mois.labels}
              values={graphiques.recettes_par_mois.values}
              color="bg-blue-600"
              formatValue={(v) => fmt(v)}
            />
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(["effectifs", "financier", "pedagogique", "presence", "annuel"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium capitalize ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "annuel" ? "Annuel (DRE)" : t}
          </button>
        ))}
      </div>

      {(tab === "financier" || tab === "presence") && (
        <div className="flex flex-wrap gap-3">
          <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
        </div>
      )}

      {tab === "effectifs" && effectifs && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Total — {effectifs.annee_libelle}</p>
              <p className="text-2xl font-bold">{effectifs.stats.total_eleves}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Garçons</p>
              <p className="text-2xl font-bold text-blue-700">{effectifs.stats.total_garcons}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Filles</p>
              <p className="text-2xl font-bold text-pink-700">{effectifs.stats.total_filles}</p>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left">Classe</th>
                  <th className="px-4 py-3 text-left">Niveau</th>
                  <th className="px-4 py-3 text-left">Effectif</th>
                  <th className="px-4 py-3 text-left">Capacité</th>
                </tr>
              </thead>
              <tbody>
                {effectifs.par_classe.map((c) => (
                  <tr key={c.id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{c.nom}</td>
                    <td className="px-4 py-2">{c.niveau_libelle}</td>
                    <td className="px-4 py-2 font-medium">{c.effectif}</td>
                    <td className="px-4 py-2">{c.capacite_max}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "financier" && financier && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-emerald-700">Recettes</p>
            <p className="text-xl font-bold text-emerald-800">{fmt(financier.total_recettes)}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-red-700">Dépenses</p>
            <p className="text-xl font-bold text-red-800">{fmt(financier.total_depenses)}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">Solde</p>
            <p className="text-xl font-bold">{fmt(financier.solde)}</p>
          </div>
        </div>
      )}

      {tab === "pedagogique" && pedagogique && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <p className="border-b border-slate-100 px-4 py-3 text-sm font-medium">{pedagogique.periode_libelle}</p>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Classe</th>
                <th className="px-4 py-3 text-left">Effectif</th>
                <th className="px-4 py-3 text-left">Moyenne</th>
                <th className="px-4 py-3 text-left">Réussite</th>
                <th className="px-4 py-3 text-left">Meilleur</th>
              </tr>
            </thead>
            <tbody>
              {pedagogique.classes.map((c) => (
                <tr key={c.classe_id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{c.classe_nom}</td>
                  <td className="px-4 py-2">{c.effectif}</td>
                  <td className="px-4 py-2">{c.moyenne_classe ? Number(c.moyenne_classe).toFixed(2) : "—"}</td>
                  <td className="px-4 py-2">{c.taux_reussite ? `${Number(c.taux_reussite).toFixed(1)} %` : "—"}</td>
                  <td className="px-4 py-2">{c.meilleur_eleve ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "presence" && presence && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Taux présence</p>
              <p className="text-2xl font-bold">{presence.taux_presence_global != null ? `${presence.taux_presence_global} %` : "—"}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-red-700">Absences</p>
              <p className="text-2xl font-bold">{presence.jours_absents_total}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-amber-700">Retards</p>
              <p className="text-2xl font-bold">{presence.jours_retards_total}</p>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left">Classe</th>
                  <th className="px-4 py-3 text-left">Absences</th>
                  <th className="px-4 py-3 text-left">Retards</th>
                  <th className="px-4 py-3 text-left">Taux</th>
                </tr>
              </thead>
              <tbody>
                {presence.par_classe.map((c) => (
                  <tr key={c.classe_id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{c.classe_nom}</td>
                    <td className="px-4 py-2">{c.jours_absents}</td>
                    <td className="px-4 py-2">{c.jours_retards}</td>
                    <td className="px-4 py-2">{c.taux_presence != null ? `${c.taux_presence} %` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "annuel" && annuel && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900">{annuel.etablissement}</h3>
          <p className="text-sm text-slate-600">Année {annuel.annee_libelle} — Rapport DRE / Inspection</p>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2">
            <Item label="Effectif total" value={String(annuel.total_eleves)} />
            <Item label="Classes" value={String(annuel.total_classes)} />
            <Item label="Recettes" value={fmt(annuel.total_recettes)} />
            <Item label="Dépenses" value={fmt(annuel.total_depenses)} />
            <Item label="Solde" value={fmt(annuel.solde_financier)} />
            <Item label="Moyenne établissement" value={annuel.moyenne_generale_etablissement ? Number(annuel.moyenne_generale_etablissement).toFixed(2) : "—"} />
            <Item label="Taux réussite" value={annuel.taux_reussite_global ? `${Number(annuel.taux_reussite_global).toFixed(1)} %` : "—"} />
            <Item label="Taux présence" value={annuel.taux_presence_annuel != null ? `${annuel.taux_presence_annuel} %` : "—"} />
            <Item label="Impayés" value={`${annuel.nombre_impayes} élève(s)`} />
          </dl>
        </div>
      )}
    </div>
  );
}

function Item({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="mt-1 font-semibold text-slate-900">{value}</dd>
    </div>
  );
}
