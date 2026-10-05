"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { listClasseEffectifs } from "@/lib/api/classes";
import { getStatsEffectifs } from "@/lib/api/eleves";
import {
  createClasse,
  deleteClasse,
  listAnnees,
  listNiveaux,
  updateClasse,
} from "@/lib/api/parametrage";
import { anneesForClassesSelect, defaultAnneeClasseId } from "@/lib/anneesScolaires";
import { ApiError } from "@/lib/api/client";
import { canManageClasses, getToken } from "@/lib/auth/session";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { IconActionButton, IconActionLink } from "@/components/ui/IconAction";
import type { ClasseEffectif, EffectifStats } from "@/types/classe";
import type { AnneeScolaire, Niveau } from "@/types/parametrage";

export default function ClassesPage() {
  const [classes, setClasses] = useState<ClasseEffectif[]>([]);
  const [stats, setStats] = useState<EffectifStats | null>(null);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [anneesOptions, setAnneesOptions] = useState<AnneeScolaire[]>([]);
  const [anneeId, setAnneeId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; nom: string } | null>(null);
  const [form, setForm] = useState({
    nom: "",
    salle: "",
    capacite_max: "40",
    niveau_id: "",
  });

  const canManage = canManageClasses();

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    listAnnees(token)
      .then((all) => {
        const options = anneesForClassesSelect(all);
        setAnneesOptions(options.length > 0 ? options : all);
        setAnneeId((current) => current || defaultAnneeClasseId(all));
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger les années scolaires");
      });
  }, []);

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !anneeId) return;
    setLoading(true);
    setError(null);
    try {
      const [effectifs, effectifStats, niveauxData] = await Promise.all([
        listClasseEffectifs(token, anneeId),
        getStatsEffectifs(token, anneeId),
        listNiveaux(token),
      ]);
      setClasses(effectifs);
      setStats(effectifStats);
      setNiveaux(niveauxData);
      setForm((f) => ({
        ...f,
        niveau_id: f.niveau_id || niveauxData[0]?.id || "",
      }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [anneeId]);

  useEffect(() => {
    load();
  }, [load]);

  const anneeLibelle = anneesOptions.find((a) => a.id === anneeId)?.libelle ?? "";

  function openCreate() {
    setEditingId(null);
    setForm({
      nom: "",
      salle: "",
      capacite_max: "40",
      niveau_id: niveaux[0]?.id ?? "",
    });
    setShowForm(true);
  }

  function openEdit(c: ClasseEffectif) {
    setShowForm(false);
    setEditingId(c.id);
    setForm({
      nom: c.nom,
      salle: c.salle ?? "",
      capacite_max: String(c.capacite_max),
      niveau_id: c.niveau_id || niveaux[0]?.id || "",
    });
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const token = getToken();
    if (!token || !canManage || !anneeId) return;
    setSaving(true);
    setError(null);
    try {
      const payload = {
        nom: form.nom.trim(),
        salle: form.salle.trim() || undefined,
        capacite_max: Number(form.capacite_max) || 40,
        niveau_id: form.niveau_id,
      };
      if (editingId) {
        await updateClasse(token, editingId, payload);
        setEditingId(null);
      } else {
        await createClasse(token, { ...payload, annee_scolaire_id: anneeId });
        setShowForm(false);
      }
      setForm({ nom: "", salle: "", capacite_max: "40", niveau_id: niveaux[0]?.id ?? "" });
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Enregistrement impossible");
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    const token = getToken();
    if (!token || !deleteTarget) return;
    setSaving(true);
    setError(null);
    try {
      await deleteClasse(token, deleteTarget.id);
      setDeleteTarget(null);
      if (editingId === deleteTarget.id) setEditingId(null);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Suppression impossible");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-3">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Classes</h2>
            <p className="text-sm text-slate-500">
              Effectifs par classe{anneeLibelle ? ` — ${anneeLibelle}` : ""}
            </p>
          </div>
          {anneesOptions.length > 0 && (
            <label className="block text-sm">
              <span className="font-medium text-slate-700">Année scolaire</span>
              <select
                value={anneeId}
                onChange={(e) => setAnneeId(e.target.value)}
                className="mt-1 block min-w-[12rem] rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                {anneesOptions.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.libelle}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        {canManage && (
          <button
            type="button"
            onClick={() => (showForm ? setShowForm(false) : openCreate())}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            {showForm ? "Annuler" : "+ Nouvelle classe"}
          </button>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {(showForm || editingId) && canManage && (
        <form
          onSubmit={handleSubmit}
          className="grid gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2"
        >
          <h3 className="md:col-span-2 font-semibold text-slate-900">
            {editingId ? "Modifier la classe" : "Nouvelle classe"}
          </h3>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Nom</span>
            <input
              required
              value={form.nom}
              onChange={(e) => setForm({ ...form, nom: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              placeholder="Ex. CP1 A"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Niveau</span>
            <select
              required
              value={form.niveau_id}
              onChange={(e) => setForm({ ...form, niveau_id: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            >
              {niveaux.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.libelle}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Salle</span>
            <input
              value={form.salle}
              onChange={(e) => setForm({ ...form, salle: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Capacité max.</span>
            <input
              type="number"
              min={1}
              max={200}
              required
              value={form.capacite_max}
              onChange={(e) => setForm({ ...form, capacite_max: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <div className="flex flex-wrap gap-2 md:col-span-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              {saving ? "Enregistrement…" : "Enregistrer"}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
              }}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
            >
              Fermer
            </button>
          </div>
        </form>
      )}

      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total élèves" value={stats.total_eleves} />
          <StatCard label="Garçons" value={stats.total_garcons} />
          <StatCard label="Filles" value={stats.total_filles} />
          <StatCard label="Sans classe" value={stats.sans_classe} highlight={stats.sans_classe > 0} />
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Classe</th>
              <th className="px-4 py-3 font-medium">Niveau</th>
              <th className="px-4 py-3 font-medium">Salle</th>
              <th className="px-4 py-3 font-medium">Effectif</th>
              <th className="px-4 py-3 font-medium">Capacité</th>
              <th className="px-4 py-3 font-medium">Places restantes</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                  Chargement…
                </td>
              </tr>
            ) : classes.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                  Aucune classe
                </td>
              </tr>
            ) : (
              classes.map((c) => (
                <tr key={c.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{c.nom}</td>
                  <td className="px-4 py-3">{c.niveau_libelle}</td>
                  <td className="px-4 py-3">{c.salle ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={c.depassement ? "font-semibold text-red-600" : ""}>{c.effectif}</span>
                  </td>
                  <td className="px-4 py-3">{c.capacite_max}</td>
                  <td className="px-4 py-3">
                    {c.depassement ? (
                      <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                        Dépassement
                      </span>
                    ) : (
                      c.places_restantes
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <IconActionLink href={`/dashboard/classes/${c.id}`} label="Voir la classe" />
                      {canManage && (
                        <>
                          <IconActionButton
                            label="Modifier la classe"
                            variant="neutral"
                            icon="edit"
                            onClick={() => openEdit(c)}
                          />
                          <IconActionButton
                            label="Supprimer la classe"
                            variant="danger"
                            icon="trash"
                            onClick={() => setDeleteTarget({ id: c.id, nom: c.nom })}
                          />
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Supprimer cette classe ?"
        message={
          deleteTarget
            ? `La classe « ${deleteTarget.nom} » sera supprimée. Impossible si des élèves y sont inscrits ou si elle est utilisée ailleurs.`
            : ""
        }
        confirmLabel="Supprimer"
        danger
        loading={saving}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={() => void confirmDelete()}
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${highlight ? "border-amber-200 bg-amber-50" : "border-slate-200 bg-white"}`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}
