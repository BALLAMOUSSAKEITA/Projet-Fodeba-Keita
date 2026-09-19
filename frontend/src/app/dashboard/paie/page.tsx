"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createAvance,
  createPeriodePaie,
  downloadBulletinPaiePdf,
  genererPaie,
  getMesBulletins,
  getMasseSalariale,
  listAvances,
  listBulletinsPaie,
  listPeriodesPaie,
  payerBulletinPaie,
  validerBulletinPaie,
} from "@/lib/api/paie";
import { listPersonnel } from "@/lib/api/personnel";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { AvanceSalaire, BulletinPaie, MasseSalariale, PeriodePaie } from "@/types/paie";

type Tab = "generation" | "bulletins" | "avances" | "masse" | "mes-bulletins";

function fmt(n: number) {
  return `${Math.round(n).toLocaleString("fr-FR")} GNF`;
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function PaiePage() {
  const [tab, setTab] = useState<Tab>("generation");
  const [periodes, setPeriodes] = useState<PeriodePaie[]>([]);
  const [periodeId, setPeriodeId] = useState("");
  const [bulletins, setBulletins] = useState<BulletinPaie[]>([]);
  const [masse, setMasse] = useState<MasseSalariale | null>(null);
  const [avances, setAvances] = useState<AvanceSalaire[]>([]);
  const [mesBulletins, setMesBulletins] = useState<BulletinPaie[]>([]);
  const [personnel, setPersonnel] = useState<{ id: string; nom: string; prenoms: string }[]>([]);
  const [avanceForm, setAvanceForm] = useState({ personnel_id: "", montant: "", motif: "" });
  const [newMois, setNewMois] = useState(String(new Date().getMonth() + 1));
  const [newAnnee, setNewAnnee] = useState(String(new Date().getFullYear()));
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const canGenerate = hasPermission("payroll.generate");
  const canView = canGenerate || hasPermission("payroll.view");
  const canMesBulletins = hasPermission("grades.view_own");

  const loadPeriodes = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    const p = await listPeriodesPaie(token);
    setPeriodes(p);
    if (p.length && !periodeId) setPeriodeId(p[0].id);
  }, [periodeId]);

  const loadBulletins = useCallback(async () => {
    const token = getToken();
    if (!token || !periodeId) return;
    setBulletins(await listBulletinsPaie(token, periodeId));
  }, [periodeId]);

  useEffect(() => { loadPeriodes(); }, [loadPeriodes]);

  useEffect(() => {
    const token = getToken();
    if (!token || !canGenerate) return;
    listPersonnel(token).then((d) => {
      setPersonnel(d.items.map((p) => ({ id: p.id, nom: p.nom, prenoms: p.prenoms })));
    });
  }, [canGenerate]);

  useEffect(() => {
    if (tab === "bulletins" || tab === "generation") loadBulletins();
    if (tab === "masse" && periodeId) {
      const token = getToken();
      if (token) getMasseSalariale(token, periodeId).then(setMasse);
    }
    if (tab === "avances") {
      const token = getToken();
      if (token) listAvances(token).then(setAvances);
    }
    if (tab === "mes-bulletins") {
      const token = getToken();
      if (token) getMesBulletins(token).then(setMesBulletins);
    }
  }, [tab, periodeId, loadBulletins]);

  async function handleCreatePeriode() {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    try {
      await createPeriodePaie(token, Number(newAnnee), Number(newMois));
      await loadPeriodes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerer() {
    const token = getToken();
    if (!token || !periodeId) return;
    setLoading(true);
    try {
      await genererPaie(token, periodeId);
      await loadBulletins();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur génération");
    } finally {
      setLoading(false);
    }
  }

  async function handlePdf(b: BulletinPaie) {
    const token = getToken();
    if (!token) return;
    try {
      await downloadBulletinPaiePdf(
        token,
        b.id,
        `bulletin_${b.personnel_matricule}_${b.periode_libelle.replace(/\s+/g, "_")}.pdf`,
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur PDF");
    }
  }

  async function handlePayer(bulletinId: string) {
    const token = getToken();
    if (!token) return;
    try {
      await validerBulletinPaie(token, bulletinId);
      await payerBulletinPaie(token, bulletinId);
      await loadBulletins();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur paiement");
    }
  }

  async function handleAvance(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;
    try {
      await createAvance(token, {
        personnel_id: avanceForm.personnel_id,
        montant: Number(avanceForm.montant),
        date_avance: todayIso(),
        motif: avanceForm.motif || undefined,
      });
      setAvanceForm({ personnel_id: "", montant: "", motif: "" });
      setAvances(await listAvances(token));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur avance");
    }
  }

  if (!canView && !canMesBulletins) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Accès refusé.
      </div>
    );
  }

  const tabs: Tab[] = canGenerate
    ? ["generation", "bulletins", "avances", "masse"]
    : canMesBulletins
      ? ["mes-bulletins"]
      : ["bulletins"];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Paie du personnel</h2>
        <p className="mt-1 text-sm text-slate-600">Génération, bulletins, avances et masse salariale</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {canGenerate && tabs.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "generation" ? "Génération" : t === "bulletins" ? "Bulletins" : t === "avances" ? "Avances" : "Masse salariale"}
          </button>
        ))}
        {canMesBulletins && (
          <button
            type="button"
            onClick={() => setTab("mes-bulletins")}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === "mes-bulletins" ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Mes bulletins
          </button>
        )}
      </div>

      {canGenerate && (
        <select
          value={periodeId}
          onChange={(e) => setPeriodeId(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {periodes.map((p) => (
            <option key={p.id} value={p.id}>{p.libelle}</option>
          ))}
        </select>
      )}

      {tab === "generation" && canGenerate && (
        <div className="flex flex-wrap gap-3 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <input
            type="number"
            min={1}
            max={12}
            value={newMois}
            onChange={(e) => setNewMois(e.target.value)}
            className="w-20 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Mois"
          />
          <input
            type="number"
            value={newAnnee}
            onChange={(e) => setNewAnnee(e.target.value)}
            className="w-24 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Année"
          />
          <button
            type="button"
            onClick={handleCreatePeriode}
            disabled={loading}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
          >
            Nouvelle période
          </button>
          <button
            type="button"
            onClick={handleGenerer}
            disabled={loading || !periodeId}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
          >
            {loading ? "Calcul…" : "Générer la paie"}
          </button>
        </div>
      )}

      {(tab === "bulletins" || tab === "generation") && bulletins.length > 0 && (
        <BulletinsTable bulletins={bulletins} canGenerate={canGenerate} onPdf={handlePdf} onPayer={handlePayer} />
      )}

      {tab === "masse" && masse && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-4">
            <StatCard label="Bulletins" value={String(masse.nombre_bulletins)} />
            <StatCard label="Masse brute" value={fmt(Number(masse.total_brut))} />
            <StatCard label="Masse nette" value={fmt(Number(masse.total_net))} />
            <StatCard label="Reste à payer" value={fmt(Number(masse.total_a_payer))} />
          </div>
        </div>
      )}

      {tab === "avances" && canGenerate && (
        <div className="space-y-4">
          <form onSubmit={handleAvance} className="flex flex-wrap gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <select
              required
              value={avanceForm.personnel_id}
              onChange={(e) => setAvanceForm((f) => ({ ...f, personnel_id: e.target.value }))}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Employé</option>
              {personnel.map((p) => (
                <option key={p.id} value={p.id}>{p.prenoms} {p.nom}</option>
              ))}
            </select>
            <input
              type="number"
              required
              min={1}
              value={avanceForm.montant}
              onChange={(e) => setAvanceForm((f) => ({ ...f, montant: e.target.value }))}
              placeholder="Montant GNF"
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              type="text"
              value={avanceForm.motif}
              onChange={(e) => setAvanceForm((f) => ({ ...f, motif: e.target.value }))}
              placeholder="Motif"
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button type="submit" className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white">
              Enregistrer avance
            </button>
          </form>
          <table className="min-w-full rounded-xl border border-slate-200 bg-white text-sm shadow-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Employé</th>
                <th className="px-4 py-3 text-left">Montant</th>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Statut</th>
              </tr>
            </thead>
            <tbody>
              {avances.map((a) => (
                <tr key={a.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{a.personnel_prenoms} {a.personnel_nom}</td>
                  <td className="px-4 py-2">{fmt(Number(a.montant))}</td>
                  <td className="px-4 py-2">{a.date_avance}</td>
                  <td className="px-4 py-2">{a.statut}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "mes-bulletins" && (
        <BulletinsTable bulletins={mesBulletins} canGenerate={false} onPdf={handlePdf} onPayer={() => {}} />
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-lg font-bold text-slate-900">{value}</p>
    </div>
  );
}

function BulletinsTable({
  bulletins,
  canGenerate,
  onPdf,
  onPayer,
}: {
  bulletins: BulletinPaie[];
  canGenerate: boolean;
  onPdf: (b: BulletinPaie) => void;
  onPayer: (id: string) => void;
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left">Employé</th>
            <th className="px-4 py-3 text-left">Brut</th>
            <th className="px-4 py-3 text-left">Net</th>
            <th className="px-4 py-3 text-left">Statut</th>
            <th className="px-4 py-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {bulletins.map((b) => (
            <tr key={b.id} className="border-t border-slate-100">
              <td className="px-4 py-2">{b.personnel_prenoms} {b.personnel_nom}</td>
              <td className="px-4 py-2">{fmt(Number(b.brut))}</td>
              <td className="px-4 py-2 font-semibold">{fmt(Number(b.net_a_payer))}</td>
              <td className="px-4 py-2">{b.statut}</td>
              <td className="px-4 py-2">
                <div className="flex gap-2">
                  <button type="button" onClick={() => onPdf(b)} className="text-emerald-700 hover:underline">PDF</button>
                  {canGenerate && b.statut !== "paye" && (
                    <button type="button" onClick={() => onPayer(b.id)} className="text-slate-700 hover:underline">
                      Payer
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
