"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createDepense,
  downloadRapportCsv,
  downloadRapportExcel,
  getBudgetSuivi,
  getRapportFinancier,
  getTresorerie,
  listCategoriesDepense,
  listComptesTresorerie,
  listDepenses,
  listJournal,
  refuserDepense,
  soumettreDepense,
  validerDepense,
} from "@/lib/api/comptabilite";
import { getAnneeActive } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { BudgetSuivi, Depense, Ecriture, RapportFinancier, Tresorerie } from "@/types/comptabilite";
import type { CategorieDepense, CompteTresorerie } from "@/types/comptabilite";

type Tab = "depenses" | "validation" | "budget" | "rapports" | "tresorerie";

const STATUT_LABELS: Record<string, string> = {
  brouillon: "Brouillon",
  soumise: "Soumise",
  validee: "Validée",
  refusee: "Refusée",
};

function fmt(n: number | string) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function yearStart() {
  return `${new Date().getFullYear()}-01-01`;
}

export default function ComptabilitePage() {
  const [tab, setTab] = useState<Tab>("depenses");
  const [categories, setCategories] = useState<CategorieDepense[]>([]);
  const [comptes, setComptes] = useState<CompteTresorerie[]>([]);
  const [anneeId, setAnneeId] = useState("");
  const [depenses, setDepenses] = useState<Depense[]>([]);
  const [budget, setBudget] = useState<BudgetSuivi | null>(null);
  const [tresorerie, setTresorerie] = useState<Tresorerie | null>(null);
  const [rapport, setRapport] = useState<RapportFinancier | null>(null);
  const [journal, setJournal] = useState<Ecriture[]>([]);
  const [dateDebut, setDateDebut] = useState(yearStart());
  const [dateFin, setDateFin] = useState(todayIso());
  const [form, setForm] = useState({
    categorie_id: "",
    compte_tresorerie_id: "",
    libelle: "",
    montant: "",
    date_depense: todayIso(),
    reference_piece: "",
  });
  const [refusMotif, setRefusMotif] = useState("");
  const [refusId, setRefusId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canCreate = hasPermission("expenses.create");
  const canValidate = hasPermission("expenses.validate");
  const canView =
    canCreate || canValidate || hasPermission("reports.view");

  const loadBase = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    const [cats, cpts, annee] = await Promise.all([
      listCategoriesDepense(token),
      listComptesTresorerie(token),
      getAnneeActive(token),
    ]);
    setCategories(cats);
    setComptes(cpts);
    setAnneeId(annee.id);
    if (cats.length) setForm((f) => ({ ...f, categorie_id: f.categorie_id || cats[0].id }));
    if (cpts.length) setForm((f) => ({ ...f, compte_tresorerie_id: f.compte_tresorerie_id || cpts[0].id }));
  }, []);

  const loadDepenses = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setDepenses(await listDepenses(token, undefined, anneeId || undefined));
  }, [anneeId]);

  useEffect(() => {
    loadBase().catch((err) => {
      setError(err instanceof ApiError ? err.message : "Erreur chargement");
    });
  }, [loadBase]);

  useEffect(() => {
    const token = getToken();
    if (!token || !anneeId) return;
    if (tab === "depenses" || tab === "validation") loadDepenses();
    if (tab === "budget") getBudgetSuivi(token, anneeId).then(setBudget).catch(() => setBudget(null));
    if (tab === "tresorerie") getTresorerie(token).then(setTresorerie);
    if (tab === "rapports") {
      Promise.all([
        getRapportFinancier(token, dateDebut, dateFin, anneeId),
        listJournal(token, dateDebut, dateFin),
      ]).then(([r, j]) => {
        setRapport(r);
        setJournal(j);
      });
    }
  }, [tab, anneeId, dateDebut, dateFin, loadDepenses]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !canCreate) return;
    setSaving(true);
    setError(null);
    try {
      const dep = await createDepense(token, {
        categorie_id: form.categorie_id,
        compte_tresorerie_id: form.compte_tresorerie_id,
        libelle: form.libelle,
        montant: Number(form.montant),
        date_depense: form.date_depense,
        annee_scolaire_id: anneeId,
        reference_piece: form.reference_piece || undefined,
      });
      await soumettreDepense(token, dep.id);
      setForm((f) => ({ ...f, libelle: "", montant: "", reference_piece: "" }));
      await loadDepenses();
      setTab("validation");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur saisie");
    } finally {
      setSaving(false);
    }
  }

  async function handleValider(id: string) {
    const token = getToken();
    if (!token || !canValidate) return;
    try {
      await validerDepense(token, id);
      await loadDepenses();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur validation");
    }
  }

  async function handleRefuser(id: string) {
    const token = getToken();
    if (!token || !canValidate || !refusMotif.trim()) return;
    try {
      await refuserDepense(token, id, refusMotif);
      setRefusId(null);
      setRefusMotif("");
      await loadDepenses();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur refus");
    }
  }

  async function handleExport(format: "csv" | "excel") {
    const token = getToken();
    if (!token) return;
    try {
      if (format === "csv") await downloadRapportCsv(token, dateDebut, dateFin, anneeId);
      else await downloadRapportExcel(token, dateDebut, dateFin, anneeId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur export");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès à la comptabilité.
      </div>
    );
  }

  const depensesValidation = depenses.filter((d) => d.statut === "soumise");
  const depensesListe = tab === "validation" ? depensesValidation : depenses;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Comptabilité</h2>
        <p className="mt-1 text-sm text-slate-600">Dépenses, budget, trésorerie et rapports financiers</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(
          [
            ["depenses", "Dépenses"],
            ...(canValidate ? [["validation", "Validation"] as const] : []),
            ["budget", "Budget"],
            ["rapports", "Rapports"],
            ["tresorerie", "Trésorerie"],
          ] as [Tab, string][]
        ).map(([t, label]) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {label}
            {t === "validation" && depensesValidation.length > 0 && (
              <span className="ml-2 rounded-full bg-amber-400 px-2 py-0.5 text-xs text-amber-900">
                {depensesValidation.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {tab === "depenses" && canCreate && (
        <div className="grid gap-6 lg:grid-cols-2">
          <form
            onSubmit={handleCreate}
            className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h3 className="font-semibold text-slate-900">Nouvelle dépense</h3>
            <select
              required
              value={form.categorie_id}
              onChange={(e) => setForm({ ...form, categorie_id: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.libelle}</option>
              ))}
            </select>
            <input
              required
              value={form.libelle}
              onChange={(e) => setForm({ ...form, libelle: e.target.value })}
              placeholder="Libellé"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              type="number"
              required
              min={1}
              value={form.montant}
              onChange={(e) => setForm({ ...form, montant: e.target.value })}
              placeholder="Montant (GNF)"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              type="date"
              required
              value={form.date_depense}
              onChange={(e) => setForm({ ...form, date_depense: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <select
              required
              value={form.compte_tresorerie_id}
              onChange={(e) => setForm({ ...form, compte_tresorerie_id: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {comptes.map((c) => (
                <option key={c.id} value={c.id}>{c.libelle}</option>
              ))}
            </select>
            <input
              value={form.reference_piece}
              onChange={(e) => setForm({ ...form, reference_piece: e.target.value })}
              placeholder="Référence pièce (optionnel)"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              {saving ? "Enregistrement…" : "Enregistrer et soumettre"}
            </button>
          </form>

          <DepensesTable
            depenses={depensesListe}
            canValidate={false}
            onValider={() => {}}
            onRefuser={() => {}}
            refusId={null}
            refusMotif=""
            setRefusId={() => {}}
            setRefusMotif={() => {}}
          />
        </div>
      )}

      {tab === "depenses" && !canCreate && (
        <DepensesTable
          depenses={depensesListe}
          canValidate={false}
          onValider={() => {}}
          onRefuser={() => {}}
          refusId={null}
          refusMotif=""
          setRefusId={() => {}}
          setRefusMotif={() => {}}
        />
      )}

      {tab === "validation" && canValidate && (
        <DepensesTable
          depenses={depensesListe}
          canValidate
          onValider={handleValider}
          onRefuser={handleRefuser}
          refusId={refusId}
          refusMotif={refusMotif}
          setRefusId={setRefusId}
          setRefusMotif={setRefusMotif}
        />
      )}

      {tab === "budget" && budget && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Budget prévu — {budget.annee_libelle}</p>
              <p className="text-xl font-bold text-slate-900">{fmt(budget.total_prevu)}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Réalisé</p>
              <p className="text-xl font-bold text-emerald-700">{fmt(budget.total_realise)}</p>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left">Catégorie</th>
                  <th className="px-4 py-3 text-left">Prévu</th>
                  <th className="px-4 py-3 text-left">Réalisé</th>
                  <th className="px-4 py-3 text-left">Écart</th>
                  <th className="px-4 py-3 text-left">Taux</th>
                </tr>
              </thead>
              <tbody>
                {budget.lignes.map((l) => (
                  <tr key={l.categorie_id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{l.categorie_libelle}</td>
                    <td className="px-4 py-2">{fmt(l.montant_prevu)}</td>
                    <td className="px-4 py-2">{fmt(l.montant_realise)}</td>
                    <td className={`px-4 py-2 ${Number(l.ecart) < 0 ? "text-red-700" : "text-emerald-700"}`}>
                      {fmt(l.ecart)}
                    </td>
                    <td className="px-4 py-2">
                      {l.taux_realisation != null ? `${Number(l.taux_realisation).toFixed(1)} %` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "rapports" && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-end gap-3">
            <label className="text-sm">
              Du
              <input
                type="date"
                value={dateDebut}
                onChange={(e) => setDateDebut(e.target.value)}
                className="ml-2 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <label className="text-sm">
              Au
              <input
                type="date"
                value={dateFin}
                onChange={(e) => setDateFin(e.target.value)}
                className="ml-2 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <button
              type="button"
              onClick={() => handleExport("csv")}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
            >
              Export CSV
            </button>
            <button
              type="button"
              onClick={() => handleExport("excel")}
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
            >
              Export Excel
            </button>
          </div>

          {rapport && (
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-emerald-700">Recettes</p>
                <p className="text-xl font-bold text-emerald-800">{fmt(rapport.total_recettes)}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-red-700">Dépenses</p>
                <p className="text-xl font-bold text-red-800">{fmt(rapport.total_depenses)}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-slate-500">Solde</p>
                <p className="text-xl font-bold text-slate-900">{fmt(rapport.solde)}</p>
              </div>
            </div>
          )}

          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Libellé</th>
                  <th className="px-4 py-3 text-left">Compte</th>
                  <th className="px-4 py-3 text-left">Montant</th>
                </tr>
              </thead>
              <tbody>
                {journal.map((e) => (
                  <tr key={e.id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{e.date_ecriture}</td>
                    <td className="px-4 py-2 capitalize">{e.type}</td>
                    <td className="px-4 py-2">{e.libelle}</td>
                    <td className="px-4 py-2">{e.compte_libelle}</td>
                    <td className={`px-4 py-2 font-medium ${e.type === "recette" ? "text-emerald-700" : "text-red-700"}`}>
                      {fmt(e.montant)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {journal.length === 0 && <p className="px-4 py-6 text-sm text-slate-500">Aucune écriture sur la période.</p>}
          </div>
        </div>
      )}

      {tab === "tresorerie" && tresorerie && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Caisse</p>
              <p className="text-xl font-bold text-slate-900">{fmt(tresorerie.total_caisse)}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-slate-500">Banque</p>
              <p className="text-xl font-bold text-slate-900">{fmt(tresorerie.total_banque)}</p>
            </div>
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
              <p className="text-xs text-emerald-700">Total</p>
              <p className="text-xl font-bold text-emerald-900">{fmt(tresorerie.total_general)}</p>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left">Compte</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Solde initial</th>
                  <th className="px-4 py-3 text-left">Solde actuel</th>
                </tr>
              </thead>
              <tbody>
                {tresorerie.comptes.map((c) => (
                  <tr key={c.id} className="border-t border-slate-100">
                    <td className="px-4 py-2">{c.libelle}</td>
                    <td className="px-4 py-2 capitalize">{c.type}</td>
                    <td className="px-4 py-2">{fmt(c.solde_initial)}</td>
                    <td className="px-4 py-2 font-semibold">{fmt(c.solde_actuel ?? c.solde_initial)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function DepensesTable({
  depenses,
  canValidate,
  onValider,
  onRefuser,
  refusId,
  refusMotif,
  setRefusId,
  setRefusMotif,
}: {
  depenses: Depense[];
  canValidate: boolean;
  onValider: (id: string) => void;
  onRefuser: (id: string) => void;
  refusId: string | null;
  refusMotif: string;
  setRefusId: (id: string | null) => void;
  setRefusMotif: (v: string) => void;
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left">Date</th>
            <th className="px-4 py-3 text-left">Libellé</th>
            <th className="px-4 py-3 text-left">Catégorie</th>
            <th className="px-4 py-3 text-left">Montant</th>
            <th className="px-4 py-3 text-left">Statut</th>
            {canValidate && <th className="px-4 py-3 text-left">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {depenses.map((d) => (
            <tr key={d.id} className="border-t border-slate-100">
              <td className="px-4 py-2">{d.date_depense}</td>
              <td className="px-4 py-2">{d.libelle}</td>
              <td className="px-4 py-2">{d.categorie_libelle}</td>
              <td className="px-4 py-2 font-medium">{fmt(d.montant)}</td>
              <td className="px-4 py-2">
                <span className={`rounded-full px-2 py-0.5 text-xs ${
                  d.statut === "validee" ? "bg-emerald-100 text-emerald-800"
                    : d.statut === "soumise" ? "bg-amber-100 text-amber-800"
                      : d.statut === "refusee" ? "bg-red-100 text-red-800"
                        : "bg-slate-100 text-slate-700"
                }`}>
                  {STATUT_LABELS[d.statut] ?? d.statut}
                </span>
              </td>
              {canValidate && d.statut === "soumise" && (
                <td className="px-4 py-2">
                  {refusId === d.id ? (
                    <div className="flex flex-col gap-2">
                      <input
                        value={refusMotif}
                        onChange={(e) => setRefusMotif(e.target.value)}
                        placeholder="Motif du refus"
                        className="rounded border border-slate-300 px-2 py-1 text-xs"
                      />
                      <div className="flex gap-2">
                        <button type="button" onClick={() => onRefuser(d.id)} className="text-xs text-red-700 hover:underline">
                          Confirmer refus
                        </button>
                        <button type="button" onClick={() => setRefusId(null)} className="text-xs text-slate-500 hover:underline">
                          Annuler
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3">
                      <button type="button" onClick={() => onValider(d.id)} className="text-emerald-700 hover:underline">
                        Valider
                      </button>
                      <button type="button" onClick={() => setRefusId(d.id)} className="text-red-700 hover:underline">
                        Refuser
                      </button>
                    </div>
                  )}
                </td>
              )}
              {canValidate && d.statut !== "soumise" && <td className="px-4 py-2">—</td>}
            </tr>
          ))}
        </tbody>
      </table>
      {depenses.length === 0 && (
        <p className="px-4 py-6 text-sm text-slate-500">Aucune dépense.</p>
      )}
    </div>
  );
}
