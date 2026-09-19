"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  affecterClasse,
  desactiverEleve,
  downloadAttestationScolarite,
  downloadCertificatTransfert,
  getEleve,
  getHistorique,
  reinscrireEleve,
  transfertSortant,
} from "@/lib/api/eleves";
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
  const id = params.id as string;
  const [eleve, setEleve] = useState<Eleve | null>(null);
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
          <h3 className="mb-4 font-semibold text-slate-900">Informations personnelles</h3>
          <dl className="space-y-2 text-sm">
            <Row label="Sexe" value={eleve.sexe === "M" ? "Garçon" : "Fille"} />
            <Row label="Date de naissance" value={eleve.date_naissance} />
            <Row label="Lieu de naissance" value={eleve.lieu_naissance} />
            <Row label="Nationalité" value={eleve.nationalite} />
            <Row label="Adresse" value={eleve.adresse} />
            <Row label="Statut" value={eleve.statut} />
          </dl>
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
              <p className="font-medium text-slate-900">{TYPE_TUTEUR[t.type] ?? t.type}</p>
              <p>{t.prenoms} {t.nom}</p>
              <p className="text-slate-600">{t.telephone}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
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
