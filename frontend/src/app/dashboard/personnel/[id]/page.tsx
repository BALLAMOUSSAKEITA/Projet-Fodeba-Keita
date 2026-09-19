"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  addAffectation,
  addConge,
  addContrat,
  addDiplome,
  getPersonnel,
  setTitulaire,
  updateCongeStatut,
} from "@/lib/api/personnel";
import { listClasses, listMatieres } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Personnel } from "@/types/personnel";
import type { Classe, Matiere } from "@/types/parametrage";

const TYPE_CONTRAT: Record<string, string> = {
  cdi: "CDI",
  cdd: "CDD",
  vacataire: "Vacataire",
};

const TYPE_CONGE: Record<string, string> = {
  conge: "Congé",
  maladie: "Maladie",
  permission: "Permission",
  absence: "Absence",
};

export default function PersonnelDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [personnel, setPersonnel] = useState<Personnel | null>(null);
  const [classes, setClasses] = useState<Classe[]>([]);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [error, setError] = useState<string | null>(null);
  const canManage = hasPermission("personnel.manage");

  const load = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      const [data, classesData, matieresData] = await Promise.all([
        getPersonnel(token, id),
        listClasses(token),
        listMatieres(token),
      ]);
      setPersonnel(data);
      setClasses(classesData);
      setMatieres(matieresData);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Personnel introuvable");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function reload(fn: () => Promise<Personnel>) {
    setError(null);
    try {
      setPersonnel(await fn());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }

  if (!personnel && !error) {
    return <p className="text-sm text-slate-500">Chargement...</p>;
  }

  if (error && !personnel) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>;
  }

  if (!personnel) return null;

  const isEnseignant = personnel.categorie === "enseignant";

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <Link href="/dashboard/personnel" className="text-sm text-emerald-700 hover:underline">
          ← Retour à l&apos;annuaire
        </Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">
          {personnel.prenoms} {personnel.nom}
        </h2>
        <p className="font-mono text-sm text-slate-500">
          {personnel.matricule} · {isEnseignant ? "Enseignant" : personnel.fonction}
        </p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold">Informations</h3>
          <dl className="space-y-2 text-sm">
            <Row label="Téléphone" value={personnel.telephone} />
            <Row label="Email" value={personnel.email} />
            <Row label="Spécialité" value={personnel.specialite} />
            <Row label="Date embauche" value={personnel.date_embauche} />
            <Row label="Statut" value={personnel.statut} />
          </dl>
        </section>

        {isEnseignant && personnel.classes_titulaire.length > 0 && (
          <section className="rounded-xl border border-emerald-100 bg-emerald-50 p-6">
            <h3 className="mb-2 font-semibold text-emerald-900">Titulaire de classe</h3>
            <ul className="text-sm text-emerald-800">
              {personnel.classes_titulaire.map((c) => (
                <li key={c.id}>{c.nom}</li>
              ))}
            </ul>
          </section>
        )}
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold">Diplômes ({personnel.diplomes.length})</h3>
        {personnel.diplomes.length === 0 ? (
          <p className="text-sm text-slate-500">Aucun diplôme enregistré</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {personnel.diplomes.map((d) => (
              <li key={d.id} className="rounded-lg bg-slate-50 p-3">
                <span className="font-medium">{d.libelle}</span>
                {d.niveau && <span className="text-slate-600"> — {d.niveau}</span>}
                {d.etablissement && <p className="text-slate-500">{d.etablissement}</p>}
              </li>
            ))}
          </ul>
        )}
        {canManage && (
          <DiplomeForm
            onSubmit={(data) => {
              const token = getToken();
              if (!token) return;
              reload(() => addDiplome(token, id, data));
            }}
          />
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold">Contrats ({personnel.contrats.length})</h3>
        {personnel.contrats.map((c) => (
          <div key={c.id} className="mb-2 rounded-lg bg-slate-50 p-3 text-sm">
            <span className="font-medium">{TYPE_CONTRAT[c.type_contrat] ?? c.type_contrat}</span>
            <span className="text-slate-600">
              {" "}— {c.date_debut}{c.date_fin ? ` → ${c.date_fin}` : ""}
            </span>
            {c.salaire_mensuel && (
              <span className="ml-2 text-slate-500">{Number(c.salaire_mensuel).toLocaleString()} GNF</span>
            )}
          </div>
        ))}
        {canManage && (
          <ContratForm
            onSubmit={(data) => {
              const token = getToken();
              if (!token) return;
              reload(() => addContrat(token, id, data));
            }}
          />
        )}
      </section>

      {isEnseignant && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold">Affectations pédagogiques</h3>
          {personnel.affectations.length === 0 ? (
            <p className="mb-4 text-sm text-slate-500">Aucune affectation</p>
          ) : (
            <ul className="mb-4 space-y-2 text-sm">
              {personnel.affectations.map((a) => (
                <li key={a.id} className="rounded-lg bg-slate-50 p-3">
                  {a.classe?.nom ?? "—"} — {a.matiere?.libelle ?? "—"}
                </li>
              ))}
            </ul>
          )}
          {canManage && (
            <AffectationForm
              classes={classes}
              matieres={matieres}
              onAffectation={(classeId, matiereId) => {
                const token = getToken();
                if (!token) return;
                reload(() => addAffectation(token, id, { classe_id: classeId, matiere_id: matiereId }));
              }}
              onTitulaire={(classeId) => {
                const token = getToken();
                if (!token) return;
                reload(() => setTitulaire(token, id, classeId));
              }}
            />
          )}
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold">Congés & absences</h3>
        {personnel.conges.map((c) => (
          <div key={c.id} className="mb-2 flex flex-wrap items-center justify-between gap-2 rounded-lg bg-slate-50 p-3 text-sm">
            <div>
              <span className="font-medium">{TYPE_CONGE[c.type] ?? c.type}</span>
              <span className="text-slate-600"> — {c.date_debut} → {c.date_fin}</span>
              {c.motif && <p className="text-slate-500">{c.motif}</p>}
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded px-2 py-0.5 text-xs font-medium ${
                c.statut === "approuve" ? "bg-emerald-100 text-emerald-700"
                  : c.statut === "refuse" ? "bg-red-100 text-red-700"
                    : "bg-amber-100 text-amber-700"
              }`}>
                {c.statut}
              </span>
              {canManage && c.statut === "demande" && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      const token = getToken();
                      if (!token) return;
                      reload(() => updateCongeStatut(token, id, c.id, "approuve"));
                    }}
                    className="text-xs text-emerald-700 hover:underline"
                  >
                    Approuver
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const token = getToken();
                      if (!token) return;
                      reload(() => updateCongeStatut(token, id, c.id, "refuse"));
                    }}
                    className="text-xs text-red-700 hover:underline"
                  >
                    Refuser
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
        <CongeForm
          onSubmit={(data) => {
            const token = getToken();
            if (!token) return;
            reload(() => addConge(token, id, data));
          }}
        />
      </section>
    </div>
  );
}

function DiplomeForm({ onSubmit }: { onSubmit: (d: { libelle: string; niveau?: string }) => void }) {
  const [libelle, setLibelle] = useState("");
  const [niveau, setNiveau] = useState("");
  return (
    <form
      className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ libelle, niveau: niveau || undefined });
        setLibelle("");
        setNiveau("");
      }}
    >
      <input placeholder="Intitulé du diplôme *" value={libelle} onChange={(e) => setLibelle(e.target.value)} required className="min-w-[180px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <input placeholder="Niveau" value={niveau} onChange={(e) => setNiveau(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <button type="submit" className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Ajouter</button>
    </form>
  );
}

function ContratForm({
  onSubmit,
}: {
  onSubmit: (d: { type_contrat: string; date_debut: string; date_fin?: string; salaire_mensuel?: number }) => void;
}) {
  const [type, setType] = useState("cdi");
  const [debut, setDebut] = useState("");
  const [fin, setFin] = useState("");
  const [salaire, setSalaire] = useState("");
  return (
    <form
      className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          type_contrat: type,
          date_debut: debut,
          date_fin: fin || undefined,
          salaire_mensuel: salaire ? Number(salaire) : undefined,
        });
        setDebut("");
        setFin("");
        setSalaire("");
      }}
    >
      <select value={type} onChange={(e) => setType(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
        <option value="cdi">CDI</option>
        <option value="cdd">CDD</option>
        <option value="vacataire">Vacataire</option>
      </select>
      <input type="date" value={debut} onChange={(e) => setDebut(e.target.value)} required className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <input type="date" value={fin} onChange={(e) => setFin(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <input placeholder="Salaire GNF" value={salaire} onChange={(e) => setSalaire(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <button type="submit" className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Ajouter contrat</button>
    </form>
  );
}

function AffectationForm({
  classes,
  matieres,
  onAffectation,
  onTitulaire,
}: {
  classes: Classe[];
  matieres: Matiere[];
  onAffectation: (classeId: string, matiereId: string) => void;
  onTitulaire: (classeId: string) => void;
}) {
  const [classeId, setClasseId] = useState(classes[0]?.id ?? "");
  const [matiereId, setMatiereId] = useState(matieres[0]?.id ?? "");
  return (
    <div className="space-y-3 border-t border-slate-100 pt-4">
      <div className="flex flex-wrap gap-2">
        <select value={classeId} onChange={(e) => setClasseId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
        </select>
        <select value={matiereId} onChange={(e) => setMatiereId(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {matieres.map((m) => <option key={m.id} value={m.id}>{m.libelle}</option>)}
        </select>
        <button
          type="button"
          onClick={() => onAffectation(classeId, matiereId)}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
        >
          Affecter
        </button>
        <button
          type="button"
          onClick={() => onTitulaire(classeId)}
          className="rounded-lg border border-emerald-200 px-4 py-2 text-sm text-emerald-700 hover:bg-emerald-50"
        >
          Définir titulaire
        </button>
      </div>
    </div>
  );
}

function CongeForm({
  onSubmit,
}: {
  onSubmit: (d: { type: string; date_debut: string; date_fin: string; motif?: string }) => void;
}) {
  const [type, setType] = useState("conge");
  const [debut, setDebut] = useState("");
  const [fin, setFin] = useState("");
  const [motif, setMotif] = useState("");
  return (
    <form
      className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4"
      onSubmit={(e: FormEvent) => {
        e.preventDefault();
        onSubmit({ type, date_debut: debut, date_fin: fin, motif: motif || undefined });
        setDebut("");
        setFin("");
        setMotif("");
      }}
    >
      <select value={type} onChange={(e) => setType(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
        <option value="conge">Congé</option>
        <option value="maladie">Maladie</option>
        <option value="permission">Permission</option>
        <option value="absence">Absence</option>
      </select>
      <input type="date" value={debut} onChange={(e) => setDebut(e.target.value)} required className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <input type="date" value={fin} onChange={(e) => setFin(e.target.value)} required className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <input placeholder="Motif" value={motif} onChange={(e) => setMotif(e.target.value)} className="min-w-[120px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      <button type="submit" className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Déclarer</button>
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
