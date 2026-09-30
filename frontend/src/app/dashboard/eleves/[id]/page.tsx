"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  addTuteur,
  affecterClasse,
  deleteEleve,
  deleteTuteur,
  desactiverEleve,
  downloadAttestationScolarite,
  downloadCertificatTransfert,
  getEleve,
  getHistorique,
  reinscrireEleve,
  transfertSortant,
  updateEleve,
  updateTuteur,
} from "@/lib/api/eleves";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { CrudActions } from "@/components/ui/CrudActions";
import { listClasses, listNiveaux } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { HistoriqueScolaire } from "@/types/classe";
import type { Eleve } from "@/types/eleve";
import type { Classe, Niveau } from "@/types/parametrage";

const TYPE_TUTEUR: Record<string, string> = {
  pere: "Père",
  mere: "Mère",
  tuteur: "Tuteur légal",
};

export default function EleveDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [eleve, setEleve] = useState<Eleve | null>(null);
  const [editForm, setEditForm] = useState({
    nom: "",
    prenoms: "",
    sexe: "M",
    date_naissance: "",
    lieu_naissance: "",
    nationalite: "",
    adresse: "",
  });
  const [editingInfo, setEditingInfo] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [editingTuteurId, setEditingTuteurId] = useState<string | null>(null);
  const [newTuteur, setNewTuteur] = useState({
    type: "pere",
    nom: "",
    prenoms: "",
    telephone: "",
  });
  const [historique, setHistorique] = useState<HistoriqueScolaire | null>(null);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [classes, setClasses] = useState<Classe[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const canEnroll = hasPermission("students.enroll");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      const [data, niveauxData, classesData, hist] = await Promise.all([
        getEleve(token, id),
        listNiveaux(token),
        listClasses(token),
        getHistorique(token, id),
      ]);
      setEleve(data);
      setEditForm({
        nom: data.nom,
        prenoms: data.prenoms,
        sexe: data.sexe,
        date_naissance: data.date_naissance,
        lieu_naissance: data.lieu_naissance ?? "",
        nationalite: data.nationalite ?? "",
        adresse: data.adresse ?? "",
      });
      setNiveaux(niveauxData);
      setClasses(classesData);
      setHistorique(hist);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Élève introuvable");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function runAction(fn: () => Promise<void>) {
    setActionLoading(true);
    setError(null);
    try {
      await fn();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setActionLoading(false);
    }
  }

  if (!eleve && !error) {
    return <p className="text-sm text-slate-500">Chargement...</p>;
  }

  if (error && !eleve) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>;
  }

  if (!eleve) return null;

  const inscription = eleve.inscriptions[0];
  const classesNiveau = classes.filter((c) => c.niveau_id === inscription?.niveau_id);
  const isActif = eleve.statut === "actif";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/dashboard/eleves" className="text-sm text-emerald-700 hover:underline">
            ← Retour à la liste
          </Link>
          <h2 className="mt-2 text-2xl font-bold text-slate-900">
            {eleve.prenoms} {eleve.nom}
          </h2>
          <p className="font-mono text-sm text-slate-500">{eleve.matricule}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() =>
              runAction(async () => {
                const token = getToken();
                if (!token) return;
                await downloadAttestationScolarite(token, id, eleve.matricule);
              })
            }
            disabled={actionLoading}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
          >
            Attestation scolarité
          </button>
        </div>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between gap-2">
            <h3 className="font-semibold text-slate-900">Informations personnelles</h3>
            {canEnroll && (
              <CrudActions
                onEdit={() => setEditingInfo((v) => !v)}
                editLabel={editingInfo ? "Annuler" : "Modifier"}
              />
            )}
          </div>
          {editingInfo && canEnroll ? (
            <form
              className="space-y-3 text-sm"
              onSubmit={(e) => {
                e.preventDefault();
                runAction(async () => {
                  const token = getToken();
                  if (!token) return;
                  await updateEleve(token, id, editForm);
                  setEditingInfo(false);
                });
              }}
            >
              <EditField label="Nom" value={editForm.nom} onChange={(v) => setEditForm({ ...editForm, nom: v })} />
              <EditField label="Prénoms" value={editForm.prenoms} onChange={(v) => setEditForm({ ...editForm, prenoms: v })} />
              <label className="block">
                <span className="text-slate-500">Sexe</span>
                <select
                  value={editForm.sexe}
                  onChange={(e) => setEditForm({ ...editForm, sexe: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                >
                  <option value="M">Garçon</option>
                  <option value="F">Fille</option>
                </select>
              </label>
              <EditField label="Date de naissance" type="date" value={editForm.date_naissance} onChange={(v) => setEditForm({ ...editForm, date_naissance: v })} />
              <EditField label="Lieu de naissance" value={editForm.lieu_naissance} onChange={(v) => setEditForm({ ...editForm, lieu_naissance: v })} />
              <EditField label="Nationalité" value={editForm.nationalite} onChange={(v) => setEditForm({ ...editForm, nationalite: v })} />
              <EditField label="Adresse" value={editForm.adresse} onChange={(v) => setEditForm({ ...editForm, adresse: v })} />
              <button type="submit" disabled={actionLoading} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50">
                Enregistrer
              </button>
            </form>
          ) : (
            <dl className="space-y-2 text-sm">
              <Row label="Sexe" value={eleve.sexe === "M" ? "Garçon" : "Fille"} />
              <Row label="Date de naissance" value={eleve.date_naissance} />
              <Row label="Lieu de naissance" value={eleve.lieu_naissance} />
              <Row label="Nationalité" value={eleve.nationalite} />
              <Row label="Adresse" value={eleve.adresse} />
              <Row label="Statut" value={eleve.statut} />
            </dl>
          )}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Scolarité</h3>
          {inscription ? (
            <dl className="space-y-2 text-sm">
              <Row label="Niveau" value={inscription.niveau?.libelle ?? "—"} />
              <Row label="Classe" value={inscription.classe?.nom ?? "Non affecté"} />
              <Row label="Type inscription" value={inscription.type === "nouvelle" ? "Nouvelle" : "Réinscription"} />
              <Row label="Date inscription" value={inscription.date_inscription} />
            </dl>
          ) : (
            <p className="text-sm text-slate-500">Aucune inscription</p>
          )}

          {canEnroll && isActif && inscription && (
            <div className="mt-4 space-y-4 border-t border-slate-100 pt-4">
              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">Affecter en classe</p>
                <select
                  defaultValue={inscription.classe_id ?? ""}
                  disabled={actionLoading}
                  onChange={(e) => {
                    if (!e.target.value) return;
                    runAction(async () => {
                      const token = getToken();
                      if (!token) return;
                      await affecterClasse(token, id, e.target.value);
                    });
                  }}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">— Choisir une classe —</option>
                  {classesNiveau.map((c) => (
                    <option key={c.id} value={c.id}>{c.nom}</option>
                  ))}
                </select>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">Changer de niveau</p>
                <select
                  defaultValue={inscription.niveau_id}
                  disabled={actionLoading}
                  onChange={(e) =>
                    runAction(async () => {
                      const token = getToken();
                      if (!token) return;
                      await reinscrireEleve(token, id, e.target.value);
                    })
                  }
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  {niveaux.map((n) => (
                    <option key={n.id} value={n.id}>{n.libelle}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </section>
      </div>

      {canEnroll && isActif && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Transfert sortant / Désactivation</h3>
          <TransfertSortantForm
            disabled={actionLoading}
            onSubmit={(ecole, motif) =>
              runAction(async () => {
                const token = getToken();
                if (!token) return;
                await transfertSortant(token, id, { ecole_destination: ecole, motif });
                await downloadCertificatTransfert(token, id, eleve.matricule, ecole);
              })
            }
          />
          <div className="mt-4 border-t border-slate-100 pt-4">
            <DesactiverForm
              disabled={actionLoading}
              onSubmit={(motif) =>
                runAction(async () => {
                  const token = getToken();
                  if (!token) return;
                  await desactiverEleve(token, id, { motif });
                })
              }
            />
          </div>
        </section>
      )}

      {historique && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Historique scolaire</h3>
          <div className="space-y-3">
            {historique.inscriptions.map((ins) => (
              <div key={ins.id} className="rounded-lg bg-slate-50 p-3 text-sm">
                <p className="font-medium">
                  {ins.annee_scolaire?.libelle ?? "—"} — {ins.niveau?.libelle ?? "—"}
                </p>
                <p className="text-slate-600">
                  Classe : {ins.classe?.nom ?? "—"} · {ins.type} · {ins.date_inscription}
                </p>
              </div>
            ))}
            {historique.transferts.map((t) => (
              <div key={t.id} className="rounded-lg border border-amber-100 bg-amber-50 p-3 text-sm">
                <p className="font-medium">
                  Transfert {t.type === "entrant" ? "entrant" : "sortant"} — {t.ecole}
                </p>
                <p className="text-slate-600">{t.date_transfert}{t.motif ? ` · ${t.motif}` : ""}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold text-slate-900">Tuteurs ({eleve.tuteurs.length})</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          {eleve.tuteurs.map((t) => (
            <div key={t.id} className="rounded-lg bg-slate-50 p-4 text-sm">
              {editingTuteurId === t.id && canEnroll ? (
                <TuteurEditForm
                  initial={t}
                  disabled={actionLoading}
                  onCancel={() => setEditingTuteurId(null)}
                  onSave={(data) =>
                    runAction(async () => {
                      const token = getToken();
                      if (!token) return;
                      await updateTuteur(token, id, t.id, data);
                      setEditingTuteurId(null);
                    })
                  }
                />
              ) : (
                <>
                  <p className="font-medium text-slate-900">{TYPE_TUTEUR[t.type] ?? t.type}</p>
                  <p>{t.prenoms} {t.nom}</p>
                  <p className="text-slate-600">{t.telephone}</p>
                  {canEnroll && (
                    <div className="mt-2">
                      <CrudActions
                        onEdit={() => setEditingTuteurId(t.id)}
                        onDelete={() =>
                          runAction(async () => {
                            const token = getToken();
                            if (!token) return;
                            if (!window.confirm("Supprimer ce tuteur ?")) return;
                            await deleteTuteur(token, id, t.id);
                          })
                        }
                      />
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
        {canEnroll && (
          <form
            className="mt-4 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-2"
            onSubmit={(e) => {
              e.preventDefault();
              runAction(async () => {
                const token = getToken();
                if (!token) return;
                await addTuteur(token, id, newTuteur);
                setNewTuteur({ type: "pere", nom: "", prenoms: "", telephone: "" });
              });
            }}
          >
            <p className="sm:col-span-2 text-sm font-medium text-slate-700">Ajouter un tuteur</p>
            <select
              value={newTuteur.type}
              onChange={(e) => setNewTuteur({ ...newTuteur, type: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="pere">Père</option>
              <option value="mere">Mère</option>
              <option value="tuteur">Tuteur légal</option>
            </select>
            <input placeholder="Téléphone *" required value={newTuteur.telephone} onChange={(e) => setNewTuteur({ ...newTuteur, telephone: e.target.value })} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            <input placeholder="Nom *" required value={newTuteur.nom} onChange={(e) => setNewTuteur({ ...newTuteur, nom: e.target.value })} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            <input placeholder="Prénoms *" required value={newTuteur.prenoms} onChange={(e) => setNewTuteur({ ...newTuteur, prenoms: e.target.value })} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            <button type="submit" disabled={actionLoading} className="rounded-lg border border-emerald-700 px-4 py-2 text-sm text-emerald-700 hover:bg-emerald-50 sm:col-span-2 sm:w-fit">
              Ajouter
            </button>
          </form>
        )}
      </section>

      {canEnroll && (
        <section className="rounded-xl border border-red-100 bg-red-50/50 p-6">
          <h3 className="font-semibold text-red-900">Zone sensible</h3>
          <p className="mt-1 text-sm text-red-800">
            La suppression définitive n&apos;est possible que si l&apos;élève n&apos;a ni notes ni paiements enregistrés.
          </p>
          <button
            type="button"
            onClick={() => setConfirmDelete(true)}
            className="mt-3 rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
          >
            Supprimer l&apos;élève
          </button>
        </section>
      )}

      <ConfirmDialog
        open={confirmDelete}
        title="Supprimer cet élève ?"
        message="Cette action est irréversible. Les inscriptions et tuteurs seront supprimés."
        confirmLabel="Supprimer"
        danger
        loading={actionLoading}
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() =>
          runAction(async () => {
            const token = getToken();
            if (!token) return;
            await deleteEleve(token, id);
            router.push("/dashboard/eleves");
          })
        }
      />
    </div>
  );
}

function EditField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-slate-500">{label}</span>
      <input
        type={type}
        required={label === "Nom" || label === "Prénoms" || label === "Date de naissance"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
      />
    </label>
  );
}

function TuteurEditForm({
  initial,
  disabled,
  onCancel,
  onSave,
}: {
  initial: { type: string; nom: string; prenoms: string; telephone: string };
  disabled: boolean;
  onCancel: () => void;
  onSave: (data: { type: string; nom: string; prenoms: string; telephone: string }) => void;
}) {
  const [form, setForm] = useState(initial);
  return (
    <form
      className="space-y-2"
      onSubmit={(e) => {
        e.preventDefault();
        onSave(form);
      }}
    >
      <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} className="w-full rounded border border-slate-300 px-2 py-1">
        <option value="pere">Père</option>
        <option value="mere">Mère</option>
        <option value="tuteur">Tuteur</option>
      </select>
      <input value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} className="w-full rounded border px-2 py-1" />
      <input value={form.prenoms} onChange={(e) => setForm({ ...form, prenoms: e.target.value })} className="w-full rounded border px-2 py-1" />
      <input value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })} className="w-full rounded border px-2 py-1" />
      <div className="flex gap-2">
        <button type="submit" disabled={disabled} className="text-emerald-700 text-xs font-medium">Enregistrer</button>
        <button type="button" onClick={onCancel} className="text-slate-500 text-xs">Annuler</button>
      </div>
    </form>
  );
}

function TransfertSortantForm({
  onSubmit,
  disabled,
}: {
  onSubmit: (ecole: string, motif: string) => void;
  disabled: boolean;
}) {
  const [ecole, setEcole] = useState("");
  const [motif, setMotif] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(ecole, motif);
      }}
      className="grid gap-3 sm:grid-cols-3"
    >
      <input
        placeholder="École de destination *"
        value={ecole}
        onChange={(e) => setEcole(e.target.value)}
        required
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm sm:col-span-2"
      />
      <input
        placeholder="Motif"
        value={motif}
        onChange={(e) => setMotif(e.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-lg border border-red-200 px-4 py-2 text-sm text-red-700 hover:bg-red-50 disabled:opacity-50 sm:col-span-3 sm:w-fit"
      >
        Enregistrer transfert sortant
      </button>
    </form>
  );
}

function DesactiverForm({
  onSubmit,
  disabled,
}: {
  onSubmit: (motif: string) => void;
  disabled: boolean;
}) {
  const [motif, setMotif] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(motif);
      }}
      className="flex flex-wrap gap-3"
    >
      <input
        placeholder="Motif d'inactivité (abandon, décès...) *"
        value={motif}
        onChange={(e) => setMotif(e.target.value)}
        required
        className="min-w-[220px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
      >
        Désactiver l&apos;élève
      </button>
    </form>
  );
}

function Row({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-medium text-slate-900">{value || "—"}</dd>
    </div>
  );
}
