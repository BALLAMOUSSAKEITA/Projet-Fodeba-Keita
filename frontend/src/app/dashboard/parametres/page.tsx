"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import {
  getAnneeActive,
  getBareme,
  getEtablissement,
  getParametrageStatut,
  listAnnees,
  listCalendrier,
  listClasses,
  listMatieres,
  listNiveaux,
  listPeriodes,
  listReferentiels,
  listTypesFrais,
  deleteCalendrierEntry,
  deleteClasse,
  deleteMatiere,
  deletePeriode,
  deleteTypeFrais,
  updateBareme,
  updateCalendrierEntry,
  updateClasse,
  updateEtablissement,
  updateMatiere,
  updatePeriode,
  updateTypeFrais,
} from "@/lib/api/parametrage";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { CrudActions } from "@/components/ui/CrudActions";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type {
  AnneeScolaire,
  Bareme,
  CalendrierEntry,
  Classe,
  Etablissement,
  Matiere,
  Niveau,
  ParametrageStatut,
  Periode,
  Referentiel,
  TypeFrais,
} from "@/types/parametrage";

const TABS = [
  { id: "overview", label: "Vue d'ensemble" },
  { id: "etablissement", label: "Établissement" },
  { id: "annees", label: "Années scolaires" },
  { id: "niveaux", label: "Niveaux & Classes" },
  { id: "matieres", label: "Matières" },
  { id: "periodes", label: "Périodes & Barème" },
  { id: "frais", label: "Types de frais" },
  { id: "calendrier", label: "Calendrier" },
  { id: "referentiels", label: "Référentiels" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function ParametresPage() {
  const [tab, setTab] = useState<TabId>("overview");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const canManage = hasPermission("settings.manage");

  const [statut, setStatut] = useState<ParametrageStatut | null>(null);
  const [etablissement, setEtablissement] = useState<Etablissement | null>(null);
  const [anneeActive, setAnneeActive] = useState<AnneeScolaire | null>(null);
  const [annees, setAnnees] = useState<AnneeScolaire[]>([]);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [classes, setClasses] = useState<Classe[]>([]);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [periodes, setPeriodes] = useState<Periode[]>([]);
  const [bareme, setBareme] = useState<Bareme | null>(null);
  const [typesFrais, setTypesFrais] = useState<TypeFrais[]>([]);
  const [calendrier, setCalendrier] = useState<CalendrierEntry[]>([]);
  const [regions, setRegions] = useState<Referentiel[]>([]);

  const [etabForm, setEtabForm] = useState<Partial<Etablissement>>({});
  const [baremeForm, setBaremeForm] = useState<Partial<Bareme>>({});
  const [editClasse, setEditClasse] = useState<Classe | null>(null);
  const [editMatiere, setEditMatiere] = useState<Matiere | null>(null);
  const [editTypeFrais, setEditTypeFrais] = useState<TypeFrais | null>(null);
  const [editPeriode, setEditPeriode] = useState<Periode | null>(null);
  const [editCalendrier, setEditCalendrier] = useState<CalendrierEntry | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ kind: string; id: string; label: string } | null>(null);
  const [paramSaving, setParamSaving] = useState(false);

  const loadData = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [statutData, etabData, anneeData, anneesData, niveauxData, matieresData, fraisData] =
        await Promise.all([
          getParametrageStatut(token),
          getEtablissement(token).catch(() => null),
          getAnneeActive(token).catch(() => null),
          listAnnees(token),
          listNiveaux(token),
          listMatieres(token),
          listTypesFrais(token),
        ]);

      setStatut(statutData);
      setEtablissement(etabData);
      setEtabForm(etabData ?? {});
      setAnneeActive(anneeData);
      setAnnees(anneesData);
      setNiveaux(niveauxData);
      setMatieres(matieresData);
      setTypesFrais(fraisData);

      if (anneeData) {
        const [classesData, periodesData, baremeData, calData, regionsData] = await Promise.all([
          listClasses(token, anneeData.id),
          listPeriodes(token, anneeData.id),
          getBareme(token, anneeData.id).catch(() => null),
          listCalendrier(token, anneeData.id),
          listReferentiels(token, "region"),
        ]);
        setClasses(classesData);
        setPeriodes(periodesData);
        setBareme(baremeData);
        setBaremeForm(baremeData ?? {});
        setCalendrier(calData);
        setRegions(regionsData);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleSaveEtablissement() {
    const token = getToken();
    if (!token || !canManage) return;
    try {
      const updated = await updateEtablissement(token, etabForm);
      setEtablissement(updated);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de sauvegarde");
    }
  }

  async function runParamAction(fn: () => Promise<void>) {
    setParamSaving(true);
    setError(null);
    try {
      await fn();
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setParamSaving(false);
    }
  }

  async function handleConfirmDelete() {
    const token = getToken();
    if (!token || !deleteTarget || !canManage) return;
    await runParamAction(async () => {
      if (deleteTarget.kind === "classe") await deleteClasse(token, deleteTarget.id);
      if (deleteTarget.kind === "matiere") await deleteMatiere(token, deleteTarget.id);
      if (deleteTarget.kind === "frais") await deleteTypeFrais(token, deleteTarget.id);
      if (deleteTarget.kind === "periode") await deletePeriode(token, deleteTarget.id);
      if (deleteTarget.kind === "calendrier") await deleteCalendrierEntry(token, deleteTarget.id);
      setDeleteTarget(null);
    });
  }

  async function handleSaveBareme() {
    const token = getToken();
    if (!token || !canManage || !anneeActive) return;
    try {
      const updated = await updateBareme(token, anneeActive.id, {
        echelle: baremeForm.echelle,
        arrondi_decimales: baremeForm.arrondi_decimales,
        seuil_passage: baremeForm.seuil_passage,
        seuil_redoublement: baremeForm.seuil_redoublement,
      });
      setBareme(updated);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de sauvegarde");
    }
  }

  if (loading) {
    return <p className="text-sm text-slate-500">Chargement du paramétrage...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Paramétrage de l&apos;établissement</h2>
        <p className="text-sm text-slate-500">
          Groupe Scolaire Privé Fodeba Keita — configuration scolaire et financière
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {statut?.pret_pour_inscriptions && (
        <div className="rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          Configuration complète — l&apos;école est prête pour les inscriptions.
        </div>
      )}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
              tab === t.id
                ? "bg-emerald-700 text-white"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "overview" && statut && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Établissement" value={statut.etablissement_configure ? "OK" : "—"} />
          <StatCard label="Année active" value={statut.annee_active ? (anneeActive?.libelle ?? "—") : "—"} />
          <StatCard label="Niveaux" value={String(statut.niveaux_count)} />
          <StatCard label="Classes" value={String(statut.classes_count)} />
          <StatCard label="Matières" value={String(statut.matieres_count)} />
          <StatCard label="Périodes" value={String(statut.periodes_count)} />
          <StatCard label="Types de frais" value={String(statut.types_frais_count)} />
          <StatCard
            label="Prêt inscriptions"
            value={statut.pret_pour_inscriptions ? "Oui" : "Non"}
            highlight={statut.pret_pour_inscriptions}
          />
        </div>
      )}

      {tab === "etablissement" && etablissement && (
        <div className="max-w-2xl space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <Field label="Nom" value={etabForm.nom ?? ""} onChange={(v) => setEtabForm({ ...etabForm, nom: v })} disabled={!canManage} />
          <Field label="Code" value={etabForm.code ?? ""} onChange={(v) => setEtabForm({ ...etabForm, code: v })} disabled={!canManage} />
          <Field label="Adresse" value={etabForm.adresse ?? ""} onChange={(v) => setEtabForm({ ...etabForm, adresse: v })} disabled={!canManage} />
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Région" value={etabForm.region ?? ""} onChange={(v) => setEtabForm({ ...etabForm, region: v })} disabled={!canManage} />
            <Field label="Préfecture" value={etabForm.prefecture ?? ""} onChange={(v) => setEtabForm({ ...etabForm, prefecture: v })} disabled={!canManage} />
            <Field label="Commune" value={etabForm.commune ?? ""} onChange={(v) => setEtabForm({ ...etabForm, commune: v })} disabled={!canManage} />
          </div>
          <Field label="Téléphone" value={etabForm.telephone ?? ""} onChange={(v) => setEtabForm({ ...etabForm, telephone: v })} disabled={!canManage} />
          <Field label="E-mail" value={etabForm.email ?? ""} onChange={(v) => setEtabForm({ ...etabForm, email: v })} disabled={!canManage} />
          <Field label="Devise principale" value={etabForm.devise_principale ?? "GNF"} onChange={(v) => setEtabForm({ ...etabForm, devise_principale: v })} disabled={!canManage} />
          {canManage && (
            <button type="button" onClick={handleSaveEtablissement} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800">
              Enregistrer
            </button>
          )}
        </div>
      )}

      {tab === "annees" && (
        <DataTable
          headers={["Libellé", "Début", "Fin", "Statut", "Active"]}
          rows={annees.map((a) => [a.libelle, a.date_debut, a.date_fin, a.statut, a.is_active ? "Oui" : "Non"])}
        />
      )}

      {tab === "niveaux" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-3 font-semibold text-slate-900">Niveaux ({niveaux.length})</h3>
            <DataTable
              headers={["Code", "Libellé", "Type"]}
              rows={niveaux.map((n) => [n.code, n.libelle, n.type])}
            />
          </div>
          <div>
            <h3 className="mb-3 font-semibold text-slate-900">Classes ({classes.length})</h3>
            <ManageTable
              headers={["Classe", "Salle", "Capacité"]}
              rows={classes.map((c) => [c.nom, c.salle ?? "—", String(c.capacite_max)])}
              canManage={canManage}
              onEdit={(i) => setEditClasse(classes[i])}
              onDelete={(i) => setDeleteTarget({ kind: "classe", id: classes[i].id, label: classes[i].nom })}
            />
          </div>
        </div>
      )}

      {tab === "matieres" && (
        <ManageTable
          headers={["Code", "Libellé", "Coefficient", "Niveaux"]}
          rows={matieres.map((m) => [
            m.code,
            m.libelle,
            String(m.coefficient_defaut),
            m.niveaux.map((n) => n.code).join(", "),
          ])}
          canManage={canManage}
          onEdit={(i) => setEditMatiere(matieres[i])}
          onDelete={(i) => setDeleteTarget({ kind: "matiere", id: matieres[i].id, label: matieres[i].libelle })}
        />
      )}

      {tab === "periodes" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-3 font-semibold text-slate-900">Périodes</h3>
            <ManageTable
              headers={["Libellé", "Début", "Fin"]}
              rows={periodes.map((p) => [p.libelle, p.date_debut, p.date_fin])}
              canManage={canManage}
              onEdit={(i) => setEditPeriode(periodes[i])}
              onDelete={(i) => setDeleteTarget({ kind: "periode", id: periodes[i].id, label: periodes[i].libelle })}
            />
          </div>
          {bareme && (
            <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
              <h3 className="font-semibold text-slate-900">Barème de notation</h3>
              <Field label="Échelle" value={baremeForm.echelle ?? "/20"} onChange={(v) => setBaremeForm({ ...baremeForm, echelle: v })} disabled={!canManage} />
              <Field label="Seuil de passage" value={String(baremeForm.seuil_passage ?? 10)} onChange={(v) => setBaremeForm({ ...baremeForm, seuil_passage: Number(v) })} disabled={!canManage} />
              <Field label="Seuil redoublement" value={String(baremeForm.seuil_redoublement ?? 8)} onChange={(v) => setBaremeForm({ ...baremeForm, seuil_redoublement: Number(v) })} disabled={!canManage} />
              {canManage && (
                <button type="button" onClick={handleSaveBareme} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800">
                  Enregistrer le barème
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {tab === "frais" && (
        <ManageTable
          headers={["Code", "Libellé", "Description", "Actif"]}
          rows={typesFrais.map((t) => [t.code, t.libelle, t.description ?? "—", t.actif ? "Oui" : "Non"])}
          canManage={canManage}
          onEdit={(i) => setEditTypeFrais(typesFrais[i])}
          onDelete={(i) => setDeleteTarget({ kind: "frais", id: typesFrais[i].id, label: typesFrais[i].libelle })}
        />
      )}

      {tab === "calendrier" && (
        <ManageTable
          headers={["Libellé", "Début", "Fin", "Type"]}
          rows={calendrier.map((c) => [c.libelle, c.date_debut, c.date_fin, c.type])}
          canManage={canManage}
          onEdit={(i) => setEditCalendrier(calendrier[i])}
          onDelete={(i) => setDeleteTarget({ kind: "calendrier", id: calendrier[i].id, label: calendrier[i].libelle })}
        />
      )}

      {editClasse && canManage && (
        <ParamEditPanel title={`Classe — ${editClasse.nom}`} onClose={() => setEditClasse(null)} onSave={() => runParamAction(async () => {
          const token = getToken();
          if (!token) return;
          await updateClasse(token, editClasse.id, {
            nom: editClasse.nom,
            salle: editClasse.salle ?? undefined,
            capacite_max: editClasse.capacite_max,
          });
          setEditClasse(null);
        })} saving={paramSaving}>
          <Field label="Nom" value={editClasse.nom} onChange={(v) => setEditClasse({ ...editClasse, nom: v })} />
          <Field label="Salle" value={editClasse.salle ?? ""} onChange={(v) => setEditClasse({ ...editClasse, salle: v })} />
          <Field label="Capacité max" value={String(editClasse.capacite_max)} onChange={(v) => setEditClasse({ ...editClasse, capacite_max: Number(v) || 1 })} />
        </ParamEditPanel>
      )}

      {editMatiere && canManage && (
        <ParamEditPanel title={`Matière — ${editMatiere.code}`} onClose={() => setEditMatiere(null)} onSave={() => runParamAction(async () => {
          const token = getToken();
          if (!token) return;
          await updateMatiere(token, editMatiere.id, { libelle: editMatiere.libelle, coefficient_defaut: Number(editMatiere.coefficient_defaut) });
          setEditMatiere(null);
        })} saving={paramSaving}>
          <Field label="Libellé" value={editMatiere.libelle} onChange={(v) => setEditMatiere({ ...editMatiere, libelle: v })} />
          <Field label="Coefficient" value={String(editMatiere.coefficient_defaut)} onChange={(v) => setEditMatiere({ ...editMatiere, coefficient_defaut: Number(v) || 1 })} />
        </ParamEditPanel>
      )}

      {editTypeFrais && canManage && (
        <ParamEditPanel title={`Type de frais — ${editTypeFrais.code}`} onClose={() => setEditTypeFrais(null)} onSave={() => runParamAction(async () => {
          const token = getToken();
          if (!token) return;
          await updateTypeFrais(token, editTypeFrais.id, { libelle: editTypeFrais.libelle, description: editTypeFrais.description ?? undefined, actif: editTypeFrais.actif });
          setEditTypeFrais(null);
        })} saving={paramSaving}>
          <Field label="Libellé" value={editTypeFrais.libelle} onChange={(v) => setEditTypeFrais({ ...editTypeFrais, libelle: v })} />
          <Field label="Description" value={editTypeFrais.description ?? ""} onChange={(v) => setEditTypeFrais({ ...editTypeFrais, description: v })} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={editTypeFrais.actif} onChange={(e) => setEditTypeFrais({ ...editTypeFrais, actif: e.target.checked })} />
            Actif
          </label>
        </ParamEditPanel>
      )}

      {editPeriode && canManage && (
        <ParamEditPanel title={`Période — ${editPeriode.libelle}`} onClose={() => setEditPeriode(null)} onSave={() => runParamAction(async () => {
          const token = getToken();
          if (!token) return;
          await updatePeriode(token, editPeriode.id, { libelle: editPeriode.libelle, date_debut: editPeriode.date_debut, date_fin: editPeriode.date_fin });
          setEditPeriode(null);
        })} saving={paramSaving}>
          <Field label="Libellé" value={editPeriode.libelle} onChange={(v) => setEditPeriode({ ...editPeriode, libelle: v })} />
          <Field label="Date début" type="date" value={editPeriode.date_debut} onChange={(v) => setEditPeriode({ ...editPeriode, date_debut: v })} />
          <Field label="Date fin" type="date" value={editPeriode.date_fin} onChange={(v) => setEditPeriode({ ...editPeriode, date_fin: v })} />
        </ParamEditPanel>
      )}

      {editCalendrier && canManage && (
        <ParamEditPanel title={`Calendrier — ${editCalendrier.libelle}`} onClose={() => setEditCalendrier(null)} onSave={() => runParamAction(async () => {
          const token = getToken();
          if (!token) return;
          await updateCalendrierEntry(token, editCalendrier.id, { libelle: editCalendrier.libelle, date_debut: editCalendrier.date_debut, date_fin: editCalendrier.date_fin, type: editCalendrier.type });
          setEditCalendrier(null);
        })} saving={paramSaving}>
          <Field label="Libellé" value={editCalendrier.libelle} onChange={(v) => setEditCalendrier({ ...editCalendrier, libelle: v })} />
          <Field label="Date début" type="date" value={editCalendrier.date_debut} onChange={(v) => setEditCalendrier({ ...editCalendrier, date_debut: v })} />
          <Field label="Date fin" type="date" value={editCalendrier.date_fin} onChange={(v) => setEditCalendrier({ ...editCalendrier, date_fin: v })} />
          <Field label="Type" value={editCalendrier.type} onChange={(v) => setEditCalendrier({ ...editCalendrier, type: v })} />
        </ParamEditPanel>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title={`Supprimer « ${deleteTarget?.label ?? ""} » ?`}
        message="Cette action est définitive si aucune donnée scolaire n'est liée."
        confirmLabel="Supprimer"
        danger
        loading={paramSaving}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleConfirmDelete}
      />

      {tab === "referentiels" && (
        <div>
          <h3 className="mb-3 font-semibold text-slate-900">Régions de Guinée</h3>
          <DataTable
            headers={["Code", "Libellé"]}
            rows={regions.map((r) => [r.code, r.libelle])}
          />
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className={`mt-1 text-xl font-bold ${highlight ? "text-emerald-700" : "text-slate-900"}`}>{value}</p>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  disabled,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
  type?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
      />
    </div>
  );
}

function ManageTable({
  headers,
  rows,
  canManage,
  onEdit,
  onDelete,
}: {
  headers: string[];
  rows: string[][];
  canManage: boolean;
  onEdit: (index: number) => void;
  onDelete: (index: number) => void;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-600">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-3 font-medium">{h}</th>
            ))}
            {canManage && <th className="px-4 py-3 font-medium">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100">
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-3">{cell}</td>
              ))}
              {canManage && (
                <td className="px-4 py-3">
                  <CrudActions onEdit={() => onEdit(i)} onDelete={() => onDelete(i)} />
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ParamEditPanel({
  title,
  children,
  onClose,
  onSave,
  saving,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  onSave: () => void;
  saving: boolean;
}) {
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30 p-4">
      <div className="w-full max-w-md space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-lg">
        <h3 className="font-semibold text-slate-900">{title}</h3>
        {children}
        <div className="flex gap-2">
          <button type="button" disabled={saving} onClick={onSave} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50">
            Enregistrer
          </button>
          <button type="button" onClick={onClose} className="rounded-lg border border-slate-200 px-4 py-2 text-sm">
            Annuler
          </button>
        </div>
      </div>
    </div>
  );
}

function DataTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-600">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-3 font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100">
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-3">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
