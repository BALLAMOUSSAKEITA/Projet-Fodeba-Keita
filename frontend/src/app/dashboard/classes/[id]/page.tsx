"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { downloadListeClassePdf, getClasseEleves } from "@/lib/api/classes";
import { deleteClasse, listClasses, listNiveaux, updateClasse } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { canManageClasses, getToken } from "@/lib/auth/session";
import { useAnneeScolaire } from "@/components/layout/AnneeScolaireProvider";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { IconActionButton, IconActionLink } from "@/components/ui/IconAction";
import type { ClasseElevesResponse } from "@/types/classe";
import type { Niveau } from "@/types/parametrage";

export default function ClasseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [data, setData] = useState<ClasseElevesResponse | null>(null);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [form, setForm] = useState({ nom: "", salle: "", capacite_max: "40", niveau_id: "" });

  const canManage = canManageClasses();
  const { anneeId } = useAnneeScolaire();

  const load = useCallback(async () => {
    const token = getToken();
    if (!token || !anneeId) return;
    try {
      const classeData = await getClasseEleves(token, id);
      setData(classeData);

      if (canManageClasses()) {
        const niveauxData = await listNiveaux(token);
        setNiveaux(niveauxData);
        const classes = await listClasses(token, anneeId);
        const full = classes.find((c) => c.id === id);
        setForm({
          nom: full?.nom ?? classeData.classe.nom,
          salle: full?.salle ?? classeData.classe.salle ?? "",
          capacite_max: String(full?.capacite_max ?? classeData.capacite_max),
          niveau_id: full?.niveau_id ?? niveauxData[0]?.id ?? "",
        });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Classe introuvable");
    }
  }, [id, anneeId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDownloadPdf() {
    const token = getToken();
    if (!token || !data) return;
    setDownloading(true);
    try {
      const filename = `liste_${data.classe.nom.replace(/\s+/g, "_")}.pdf`;
      await downloadListeClassePdf(token, id, filename);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur PDF");
    } finally {
      setDownloading(false);
    }
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    const token = getToken();
    if (!token || !canManage) return;
    setSaving(true);
    setError(null);
    try {
      await updateClasse(token, id, {
        nom: form.nom.trim(),
        salle: form.salle.trim() || undefined,
        capacite_max: Number(form.capacite_max) || 40,
        niveau_id: form.niveau_id,
      });
      setEditing(false);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Enregistrement impossible");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    const token = getToken();
    if (!token || !canManage) return;
    setSaving(true);
    setError(null);
    try {
      await deleteClasse(token, id);
      router.push("/dashboard/classes");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Suppression impossible");
      setSaving(false);
      setDeleteOpen(false);
    }
  }

  if (!data && !error) {
    return <p className="text-sm text-slate-500">Chargement…</p>;
  }

  if (error && !data) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>;
  }

  if (!data) return null;

  const { classe, effectif, capacite_max, eleves } = data;
  const depassement = effectif > capacite_max;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/dashboard/classes" className="text-sm text-emerald-700 hover:underline">
            Retour aux classes
          </Link>
          <h2 className="mt-2 text-2xl font-bold text-slate-900">{classe.nom}</h2>
          <p className="text-sm text-slate-500">
            Salle {classe.salle ?? "—"} · {effectif}/{capacite_max} élèves
            {depassement && (
              <span className="ml-2 rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                Capacité dépassée
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {canManage && (
            <>
              <IconActionButton
                label={editing ? "Annuler la modification" : "Modifier la classe"}
                variant="neutral"
                icon="edit"
                onClick={() => setEditing(!editing)}
              />
              <IconActionButton
                label="Supprimer la classe"
                variant="danger"
                icon="trash"
                onClick={() => setDeleteOpen(true)}
              />
            </>
          )}
          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
          >
            {downloading ? "Génération…" : "Liste PDF"}
          </button>
        </div>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {editing && canManage && (
        <form
          onSubmit={handleSave}
          className="grid gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2"
        >
          <h3 className="md:col-span-2 font-semibold text-slate-900">Modifier la classe</h3>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Nom</span>
            <input
              required
              value={form.nom}
              onChange={(e) => setForm({ ...form, nom: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
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
          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              {saving ? "Enregistrement…" : "Enregistrer"}
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">N°</th>
              <th className="px-4 py-3 font-medium">Matricule</th>
              <th className="px-4 py-3 font-medium">Nom complet</th>
              <th className="px-4 py-3 font-medium">Sexe</th>
              <th className="px-4 py-3 font-medium">Naissance</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {eleves.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  Aucun élève affecté
                </td>
              </tr>
            ) : (
              eleves.map((e, i) => (
                <tr key={e.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-500">{i + 1}</td>
                  <td className="px-4 py-3 font-mono text-xs">{e.matricule}</td>
                  <td className="px-4 py-3 font-medium">
                    {e.prenoms} {e.nom}
                  </td>
                  <td className="px-4 py-3">{e.sexe === "M" ? "G" : "F"}</td>
                  <td className="px-4 py-3">{e.date_naissance}</td>
                  <td className="px-4 py-3">
                    <IconActionLink href={`/dashboard/eleves/${e.id}`} label="Voir la fiche élève" />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        open={deleteOpen}
        title="Supprimer cette classe ?"
        message={`La classe « ${classe.nom} » sera supprimée. Impossible si des élèves y sont inscrits ou si elle est utilisée ailleurs.`}
        confirmLabel="Supprimer"
        danger
        loading={saving}
        onCancel={() => setDeleteOpen(false)}
        onConfirm={() => void handleDelete()}
      />
    </div>
  );
}
