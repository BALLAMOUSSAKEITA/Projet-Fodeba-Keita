"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createDepense,
  getRapportFinancier,
  getTresorerie,
  listCategoriesDepense,
  listComptesTresorerie,
  listDepenses,
  soumettreDepense,
  validerDepense,
} from "@/lib/api/comptabilite";
import { getAnneeActive } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Depense, RapportFinancier, Tresorerie } from "@/types/comptabilite";

function fmt(n: number | string) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function ComptabilitePage() {
  const [anneeId, setAnneeId] = useState("");
  const [dateDebut, setDateDebut] = useState("");
  const [dateFin, setDateFin] = useState(todayIso());
  const [depenses, setDepenses] = useState<Depense[]>([]);
  const [rapport, setRapport] = useState<RapportFinancier | null>(null);
  const [tresorerie, setTresorerie] = useState<Tresorerie | null>(null);
  const [defaultCategorieId, setDefaultCategorieId] = useState("");
  const [defaultCompteId, setDefaultCompteId] = useState("");
  const [form, setForm] = useState({ nature: "", montant: "", date_depense: todayIso() });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canCreate = hasPermission("expenses.create");
  const canValidate = hasPermission("expenses.validate");
  const canView = canCreate || canValidate || hasPermission("reports.view");

  const loadAll = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    const annee = await getAnneeActive(token);
    setAnneeId(annee.id);
    setDateDebut(annee.date_debut);
    const [cats, cpts, deps, tres, rap] = await Promise.all([
      listCategoriesDepense(token),
      listComptesTresorerie(token),
      listDepenses(token, undefined, annee.id),
      getTresorerie(token),
      getRapportFinancier(token, annee.date_debut, todayIso(), annee.id),
    ]);
    if (cats.length) setDefaultCategorieId(cats[0].id);
    const caisse = cpts.find((c) => c.type === "caisse") ?? cpts[0];
    if (caisse) setDefaultCompteId(caisse.id);
    setDepenses(deps.filter((d) => d.statut === "validee" || d.statut === "soumise"));
    setTresorerie(tres);
    setRapport(rap);
  }, []);

  useEffect(() => {
    loadAll().catch((err) => {
      setError(err instanceof ApiError ? err.message : "Erreur chargement");
    });
  }, [loadAll]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !canCreate || !defaultCategorieId || !defaultCompteId || !anneeId) return;
    setSaving(true);
    setError(null);
    try {
      const dep = await createDepense(token, {
        categorie_id: defaultCategorieId,
        compte_tresorerie_id: defaultCompteId,
        libelle: form.nature.trim(),
        montant: Number(form.montant),
        date_depense: form.date_depense,
        annee_scolaire_id: anneeId,
      });
      await soumettreDepense(token, dep.id);
      if (canValidate) {
        await validerDepense(token, dep.id);
      }
      setForm({ nature: "", montant: "", date_depense: todayIso() });
      await loadAll();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement");
    } finally {
      setSaving(false);
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès à la comptabilité.
      </div>
    );
  }

  const entrees = rapport ? Number(rapport.total_recettes) : 0;
  const sorties = rapport ? Number(rapport.total_depenses) : 0;
  const soldeCaisse = tresorerie ? Number(tresorerie.total_caisse) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Comptabilité</h2>
        <p className="mt-1 text-sm text-slate-600">
          Dépenses diverses et vue de la caisse (année en cours)
        </p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
          <p className="text-xs font-medium text-emerald-800">Entrées (recettes)</p>
          <p className="mt-1 text-xl font-bold text-emerald-900">{fmt(entrees)}</p>
        </div>
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 shadow-sm">
          <p className="text-xs font-medium text-red-800">Sorties (dépenses)</p>
          <p className="mt-1 text-xl font-bold text-red-900">{fmt(sorties)}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-xs text-slate-500">Solde caisse</p>
          <p className="mt-1 text-xl font-bold text-slate-900">{fmt(soldeCaisse)}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {canCreate && (
          <form
            onSubmit={handleCreate}
            className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h3 className="font-semibold text-slate-900">Nouvelle dépense</h3>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Nature</span>
              <input
                required
                value={form.nature}
                onChange={(e) => setForm({ ...form, nature: e.target.value })}
                placeholder="Ex. Fournitures, électricité…"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Montant (GNF)</span>
              <input
                type="number"
                required
                min={1}
                value={form.montant}
                onChange={(e) => setForm({ ...form, montant: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Date</span>
              <input
                type="date"
                required
                value={form.date_depense}
                onChange={(e) => setForm({ ...form, date_depense: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              {saving ? "Enregistrement…" : "Enregistrer la dépense"}
            </button>
          </form>
        )}

        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-1">
          <h3 className="border-b border-slate-100 px-4 py-3 text-sm font-semibold text-slate-900">
            Dépenses enregistrées
          </h3>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Nature</th>
                <th className="px-4 py-3 text-left">Montant</th>
              </tr>
            </thead>
            <tbody>
              {depenses.map((d) => (
                <tr key={d.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{d.date_depense}</td>
                  <td className="px-4 py-2">{d.libelle}</td>
                  <td className="px-4 py-2 font-medium text-red-700">{fmt(d.montant)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {depenses.length === 0 && (
            <p className="px-4 py-6 text-sm text-slate-500">Aucune dépense pour l&apos;instant.</p>
          )}
        </div>
      </div>

      {dateDebut && (
        <p className="text-xs text-slate-500">
          Synthèse du {dateDebut} au {dateFin} (année scolaire active).
        </p>
      )}
    </div>
  );
}
