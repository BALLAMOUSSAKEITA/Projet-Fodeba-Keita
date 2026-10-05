"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createPeriodePaie,
  genererPaie,
  getMesBulletins,
  listBulletinsPaie,
  listPeriodesPaie,
  payerBulletinPaie,
  updateBulletinPaie,
  validerBulletinPaie,
} from "@/lib/api/paie";
import { addContrat, getPersonnel, listPersonnel, updateContrat } from "@/lib/api/personnel";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { BulletinPaie } from "@/types/paie";
import type { Personnel } from "@/types/personnel";

function fmt(n: number) {
  return `${Math.round(n).toLocaleString("fr-FR")} GNF`;
}

function monthValueFromDate(d = new Date()) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function parseMonth(value: string) {
  const [y, m] = value.split("-").map(Number);
  return { annee: y, mois: m };
}

type RowState = {
  personnelId: string;
  nom: string;
  prenoms: string;
  matricule: string;
  contratId: string | null;
  salaire: string;
  prime: string;
  bulletin: BulletinPaie | null;
};

export default function PaiePage() {
  const [month, setMonth] = useState(monthValueFromDate());
  const [periodeId, setPeriodeId] = useState("");
  const [rows, setRows] = useState<RowState[]>([]);
  const [mesBulletins, setMesBulletins] = useState<BulletinPaie[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [payingId, setPayingId] = useState<string | null>(null);

  const canGenerate = hasPermission("payroll.generate");
  const canMesBulletins = hasPermission("grades.view_own");

  const loadStaff = useCallback(async () => {
    const token = getToken();
    if (!token || !canGenerate) return;
    const list = await listPersonnel(token, { statut: "actif" });
    const details = await Promise.all(list.items.map((p) => getPersonnel(token, p.id)));
    setRows(details.map(personnelToRow));
  }, [canGenerate]);

  const ensurePeriode = useCallback(async () => {
    const token = getToken();
    if (!token || !canGenerate) return null;
    const { annee, mois } = parseMonth(month);
    let periodes = await listPeriodesPaie(token);
    let match = periodes.find((p) => p.annee === annee && p.mois === mois);
    if (!match) {
      match = await createPeriodePaie(token, annee, mois);
      periodes = await listPeriodesPaie(token);
    }
    setPeriodeId(match.id);
    return match.id;
  }, [canGenerate, month]);

  const refreshBulletins = useCallback(async (pid: string) => {
    const token = getToken();
    if (!token) return;
    const bulletins = await listBulletinsPaie(token, pid);
    setRows((prev) =>
      prev.map((r) => ({
        ...r,
        bulletin: bulletins.find((b) => b.personnel_id === r.personnelId) ?? null,
        prime: String(
          bulletins.find((b) => b.personnel_id === r.personnelId)?.prime_autre
            ?? r.prime
            ?? "0",
        ),
      })),
    );
  }, []);

  useEffect(() => {
    loadStaff().catch((err) => {
      setError(err instanceof ApiError ? err.message : "Erreur chargement");
    });
  }, [loadStaff]);

  useEffect(() => {
    if (!canGenerate) return;
    ensurePeriode()
      .then((pid) => {
        if (pid) return refreshBulletins(pid);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Erreur période");
      });
  }, [canGenerate, month, ensurePeriode, refreshBulletins]);

  useEffect(() => {
    if (!canMesBulletins) return;
    const token = getToken();
    if (token) getMesBulletins(token).then(setMesBulletins);
  }, [canMesBulletins]);

  async function saveSalaire(row: RowState) {
    const token = getToken();
    if (!token || !canGenerate) return;
    const salaire = Number(row.salaire);
    if (!salaire || salaire < 0) return;

    if (row.contratId) {
      await updateContrat(token, row.personnelId, row.contratId, { salaire_mensuel: salaire });
    } else {
      const today = new Date().toISOString().slice(0, 10);
      const p = await addContrat(token, row.personnelId, {
        type_contrat: "cdi",
        date_debut: today,
        salaire_mensuel: salaire,
      });
      const actif = p.contrats.find((c) => c.statut === "actif") ?? p.contrats[0];
      setRows((prev) =>
        prev.map((r) =>
          r.personnelId === row.personnelId ? { ...r, contratId: actif?.id ?? null } : r,
        ),
      );
    }
  }

  async function prepareAndPay(personnelId?: string) {
    const token = getToken();
    if (!token || !canGenerate) return;
    setLoading(true);
    setPayingId(personnelId ?? "all");
    setError(null);
    try {
      const pid = periodeId || (await ensurePeriode());
      if (!pid) return;

      const targetRows = personnelId ? rows.filter((r) => r.personnelId === personnelId) : rows;

      for (const row of targetRows) {
        if (row.salaire) await saveSalaire(row);
      }

      await genererPaie(token, pid, personnelId);

      let bulletins = await listBulletinsPaie(token, pid);
      for (const row of targetRows) {
        const b = bulletins.find((x) => x.personnel_id === row.personnelId);
        if (!b || b.statut === "paye") continue;
        const prime = Number(row.prime) || 0;
        if (prime !== Number(b.prime_autre)) {
          await updateBulletinPaie(token, b.id, { prime_autre: prime });
        }
      }

      bulletins = await listBulletinsPaie(token, pid);
      const toPay = personnelId
        ? bulletins.filter((b) => b.personnel_id === personnelId)
        : bulletins;

      for (const b of toPay) {
        if (b.statut === "paye") continue;
        await validerBulletinPaie(token, b.id);
        await payerBulletinPaie(token, b.id);
      }

      await refreshBulletins(pid);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur paiement");
    } finally {
      setLoading(false);
      setPayingId(null);
    }
  }

  const totalNet = useMemo(
    () => rows.reduce((s, r) => s + (r.bulletin ? Number(r.bulletin.net_a_payer) : 0), 0),
    [rows],
  );

  if (!canGenerate && !canMesBulletins) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Accès refusé.
      </div>
    );
  }

  if (!canGenerate) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Mes bulletins de paie</h2>
        </div>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Période</th>
                <th className="px-4 py-3 text-left">Net payé</th>
                <th className="px-4 py-3 text-left">Statut</th>
              </tr>
            </thead>
            <tbody>
              {mesBulletins.map((b) => (
                <tr key={b.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{b.periode_libelle}</td>
                  <td className="px-4 py-2 font-semibold">{fmt(Number(b.net_a_payer))}</td>
                  <td className="px-4 py-2 capitalize">{b.statut}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {mesBulletins.length === 0 && (
            <p className="px-4 py-6 text-sm text-slate-500">Aucun bulletin.</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Paie du personnel</h2>
          <p className="mt-1 text-sm text-slate-600">
            Salaires, primes et paiement mensuel
          </p>
        </div>
        <label className="text-sm font-medium text-slate-700">
          Mois
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="ml-2 rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </label>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={loading || rows.length === 0}
          onClick={() => prepareAndPay()}
          className="rounded-lg bg-emerald-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {payingId === "all" && loading ? "Paiement en cours…" : "Payer tout le personnel"}
        </button>
        <p className="text-sm text-slate-600">
          Net du mois (bulletins) : <span className="font-semibold text-slate-900">{fmt(totalNet)}</span>
        </p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left">Employé</th>
              <th className="px-4 py-3 text-left">Salaire (GNF)</th>
              <th className="px-4 py-3 text-left">Prime (GNF)</th>
              <th className="px-4 py-3 text-left">Net à payer</th>
              <th className="px-4 py-3 text-left">Statut</th>
              <th className="px-4 py-3 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.personnelId} className="border-t border-slate-100">
                <td className="px-4 py-2">
                  <span className="font-medium">{row.prenoms} {row.nom}</span>
                  <span className="ml-1 text-xs text-slate-500">{row.matricule}</span>
                </td>
                <td className="px-4 py-2">
                  <input
                    type="number"
                    min={0}
                    value={row.salaire}
                    onChange={(e) =>
                      setRows((prev) =>
                        prev.map((r) =>
                          r.personnelId === row.personnelId ? { ...r, salaire: e.target.value } : r,
                        ),
                      )
                    }
                    onBlur={() => saveSalaire(row).catch(() => {})}
                    className="w-32 rounded-lg border border-slate-300 px-2 py-1 text-sm"
                    placeholder="0"
                  />
                </td>
                <td className="px-4 py-2">
                  <input
                    type="number"
                    min={0}
                    value={row.prime}
                    onChange={(e) =>
                      setRows((prev) =>
                        prev.map((r) =>
                          r.personnelId === row.personnelId ? { ...r, prime: e.target.value } : r,
                        ),
                      )
                    }
                    className="w-28 rounded-lg border border-slate-300 px-2 py-1 text-sm"
                    placeholder="0"
                  />
                </td>
                <td className="px-4 py-2 font-medium">
                  {row.bulletin ? fmt(Number(row.bulletin.net_a_payer)) : "—"}
                </td>
                <td className="px-4 py-2 capitalize">{row.bulletin?.statut ?? "—"}</td>
                <td className="px-4 py-2">
                  <button
                    type="button"
                    disabled={loading || !row.salaire || row.bulletin?.statut === "paye"}
                    onClick={() => prepareAndPay(row.personnelId)}
                    className="text-emerald-700 hover:underline disabled:opacity-40"
                  >
                    {payingId === row.personnelId && loading ? "…" : "Payer"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && (
          <p className="px-4 py-6 text-sm text-slate-500">Aucun personnel actif.</p>
        )}
      </div>
    </div>
  );
}

function personnelToRow(p: Personnel): RowState {
  const contrat = p.contrats.find((c) => c.statut === "actif") ?? p.contrats[0];
  return {
    personnelId: p.id,
    nom: p.nom,
    prenoms: p.prenoms,
    matricule: p.matricule,
    contratId: contrat?.id ?? null,
    salaire: contrat?.salaire_mensuel != null ? String(contrat.salaire_mensuel) : "",
    prime: "0",
    bulletin: null,
  };
}
