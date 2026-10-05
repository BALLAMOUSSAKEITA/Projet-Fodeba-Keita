"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { deactivatePersonnel, deletePersonnelPermanent, listPersonnel } from "@/lib/api/personnel";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { CrudActions } from "@/components/ui/CrudActions";
import { IconActionButton, IconActionLink } from "@/components/ui/IconAction";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission, isSuperAdmin } from "@/lib/auth/session";
import type { PersonnelListItem } from "@/types/personnel";

const CATEGORIE_LABEL: Record<string, string> = {
  enseignant: "Enseignant",
  non_enseignant: "Non enseignant",
};

export default function PersonnelPage() {
  const router = useRouter();
  const [items, setItems] = useState<PersonnelListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [categorie, setCategorie] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const canManage = hasPermission("personnel.manage");
  const superAdmin = isSuperAdmin();
  const [deactivateId, setDeactivateId] = useState<string | null>(null);
  const [permanentDeleteId, setPermanentDeleteId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    try {
      const data = await listPersonnel(token, {
        search: search || undefined,
        categorie: categorie || undefined,
        statut: "actif",
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [search, categorie]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Personnel</h2>
          <p className="text-sm text-slate-500">{total} membre(s) actif(s)</p>
        </div>
        {canManage && (
          <Link
            href="/dashboard/personnel/nouveau"
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            + Ajouter
          </Link>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="flex flex-wrap gap-3">
        <input
          placeholder="Rechercher (nom, matricule)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-[220px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <select
          value={categorie}
          onChange={(e) => setCategorie(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Toutes catégories</option>
          <option value="enseignant">Enseignants</option>
          <option value="non_enseignant">Non enseignants</option>
        </select>
        <button
          type="button"
          onClick={load}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
        >
          Filtrer
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Matricule</th>
              <th className="px-4 py-3 font-medium">Nom complet</th>
              <th className="px-4 py-3 font-medium">Catégorie</th>
              <th className="px-4 py-3 font-medium">Fonction / Spécialité</th>
              <th className="px-4 py-3 font-medium">Téléphone</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">Chargement...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">Aucun personnel trouvé</td></tr>
            ) : (
              items.map((p) => (
                <tr key={p.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs">{p.matricule}</td>
                  <td className="px-4 py-3 font-medium">{p.prenoms} {p.nom}</td>
                  <td className="px-4 py-3">{CATEGORIE_LABEL[p.categorie] ?? p.categorie}</td>
                  <td className="px-4 py-3">{p.fonction ?? p.specialite ?? "—"}</td>
                  <td className="px-4 py-3">{p.telephone}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <IconActionLink href={`/dashboard/personnel/${p.id}`} label="Voir la fiche personnel" />
                      {canManage && (
                        <>
                          <CrudActions
                            onEdit={() => router.push(`/dashboard/personnel/${p.id}`)}
                            editLabel="Modifier la fiche"
                            onDelete={p.statut === "actif" ? () => setDeactivateId(p.id) : undefined}
                            deleteLabel="Désactiver"
                          />
                          {superAdmin && (
                            <IconActionButton
                              label="Supprimer définitivement"
                              icon="trash"
                              variant="danger"
                              onClick={() => setPermanentDeleteId(p.id)}
                            />
                          )}
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
        open={!!deactivateId}
        title="Désactiver ce membre du personnel ?"
        message="Il n'apparaîtra plus dans la liste des actifs. La fiche reste en base."
        confirmLabel="Désactiver"
        danger
        loading={saving}
        onCancel={() => setDeactivateId(null)}
        onConfirm={async () => {
          const token = getToken();
          if (!token || !deactivateId) return;
          setSaving(true);
          try {
            await deactivatePersonnel(token, deactivateId);
            setDeactivateId(null);
            await load();
          } catch (err) {
            setError(err instanceof ApiError ? err.message : "Erreur");
          } finally {
            setSaving(false);
          }
        }}
      />

      <ConfirmDialog
        open={!!permanentDeleteId}
        title="Supprimer définitivement ce personnel ?"
        message="Action irréversible : fiche, contrats, affectations et données liées seront effacés."
        confirmLabel="Supprimer définitivement"
        danger
        loading={saving}
        onCancel={() => setPermanentDeleteId(null)}
        onConfirm={async () => {
          const token = getToken();
          if (!token || !permanentDeleteId) return;
          setSaving(true);
          try {
            await deletePersonnelPermanent(token, permanentDeleteId);
            setPermanentDeleteId(null);
            await load();
          } catch (err) {
            setError(err instanceof ApiError ? err.message : "Erreur");
          } finally {
            setSaving(false);
          }
        }}
      />
    </div>
  );
}
