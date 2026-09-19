"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createSeance,
  downloadEdtExcel,
  downloadEdtPdf,
  getGrilleClasse,
  getGrilleEnseignant,
  listConflits,
} from "@/lib/api/edt";
import { listClasses, listMatieres } from "@/lib/api/parametrage";
import { listPersonnel } from "@/lib/api/personnel";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { GrilleEdt } from "@/types/edt";
import type { Classe, Matiere } from "@/types/parametrage";
import type { PersonnelListItem } from "@/types/personnel";

export default function EmploiDuTempsPage() {
  const [mode, setMode] = useState<"classe" | "enseignant">("classe");
  const [classes, setClasses] = useState<Classe[]>([]);
  const [enseignants, setEnseignants] = useState<PersonnelListItem[]>([]);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [selectedClasse, setSelectedClasse] = useState("");
  const [selectedEnseignant, setSelectedEnseignant] = useState("");
  const [grille, setGrille] = useState<GrilleEdt | null>(null);
  const [globalConflits, setGlobalConflits] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const canManage = hasPermission("timetable.manage");

  const loadRefs = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    const [c, p, m, conflits] = await Promise.all([
      listClasses(token),
      listPersonnel(token, { categorie: "enseignant" }),
      listMatieres(token),
      listConflits(token),
    ]);
    setClasses(c);
    setEnseignants(p.items);
    setMatieres(m);
    setGlobalConflits(conflits.total);
    if (c.length > 0 && !selectedClasse) setSelectedClasse(c[0].id);
    if (p.items.length > 0 && !selectedEnseignant) setSelectedEnseignant(p.items[0].id);
  }, [selectedClasse, selectedEnseignant]);

  const loadGrille = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      if (mode === "classe" && selectedClasse) {
        setGrille(await getGrilleClasse(token, selectedClasse));
      } else if (mode === "enseignant" && selectedEnseignant) {
        setGrille(await getGrilleEnseignant(token, selectedEnseignant));
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [mode, selectedClasse, selectedEnseignant]);

  useEffect(() => {
    loadRefs();
  }, [loadRefs]);

  useEffect(() => {
    loadGrille();
  }, [loadGrille]);

  async function handleExportPdf() {
    const token = getToken();
    if (!token || !selectedClasse) return;
    const nom = classes.find((c) => c.id === selectedClasse)?.nom ?? "classe";
    await downloadEdtPdf(token, selectedClasse, `edt_${nom.replace(/\s+/g, "_")}.pdf`);
  }

  async function handleExportExcel() {
    const token = getToken();
    if (!token || !selectedClasse) return;
    const nom = classes.find((c) => c.id === selectedClasse)?.nom ?? "classe";
    await downloadEdtExcel(token, selectedClasse, `edt_${nom.replace(/\s+/g, "_")}.xlsx`);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Emploi du temps</h2>
          <p className="text-sm text-slate-500">
            {globalConflits > 0 ? (
              <span className="font-medium text-red-600">{globalConflits} conflit(s) détecté(s)</span>
            ) : (
              "Aucun conflit global"
            )}
          </p>
        </div>
        {mode === "classe" && selectedClasse && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleExportPdf}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
            >
              Export PDF
            </button>
            <button
              type="button"
              onClick={handleExportExcel}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
            >
              Export Excel
            </button>
          </div>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-3">
        <div className="flex rounded-lg border border-slate-200 p-1">
          <button
            type="button"
            onClick={() => setMode("classe")}
            className={`rounded-md px-4 py-1.5 text-sm ${mode === "classe" ? "bg-emerald-700 text-white" : "text-slate-600"}`}
          >
            Par classe
          </button>
          <button
            type="button"
            onClick={() => setMode("enseignant")}
            className={`rounded-md px-4 py-1.5 text-sm ${mode === "enseignant" ? "bg-emerald-700 text-white" : "text-slate-600"}`}
          >
            Par enseignant
          </button>
        </div>

        {mode === "classe" ? (
          <select
            value={selectedClasse}
            onChange={(e) => setSelectedClasse(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {classes.map((c) => (
              <option key={c.id} value={c.id}>{c.nom}</option>
            ))}
          </select>
        ) : (
          <select
            value={selectedEnseignant}
            onChange={(e) => setSelectedEnseignant(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {enseignants.map((e) => (
              <option key={e.id} value={e.id}>{e.prenoms} {e.nom}</option>
            ))}
          </select>
        )}
      </div>

      {grille && grille.conflits.length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {grille.conflits.map((c, i) => (
            <p key={i}>{c.message} ({c.type})</p>
          ))}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Chargement...</p>
      ) : grille ? (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-emerald-700 text-white">
              <tr>
                <th className="px-3 py-2 text-left font-medium">Créneau</th>
                {grille.jours.map((j) => (
                  <th key={j} className="px-3 py-2 text-left font-medium">{j}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {grille.lignes.map((ligne) => (
                <tr key={ligne.creneau.id} className="border-t border-slate-100">
                  <td className="whitespace-nowrap px-3 py-2 font-medium text-slate-700">
                    {ligne.creneau.libelle}
                    <br />
                    <span className="text-xs text-slate-500">
                      {ligne.creneau.heure_debut.slice(0, 5)}-{ligne.creneau.heure_fin.slice(0, 5)}
                    </span>
                  </td>
                  {ligne.cellules.map((cell, j) => (
                    <td key={j} className="px-3 py-2 align-top">
                      {cell ? (
                        <div className="rounded-lg bg-emerald-50 p-2 text-xs">
                          <p className="font-semibold text-emerald-900">{cell.matiere?.libelle}</p>
                          {cell.personnel && (
                            <p className="text-emerald-700">{cell.personnel.prenoms} {cell.personnel.nom}</p>
                          )}
                          {cell.salle && <p className="text-slate-500">{cell.salle}</p>}
                          {mode === "classe" && cell.classe && (
                            <p className="text-slate-500">{cell.classe.nom}</p>
                          )}
                        </div>
                      ) : canManage && mode === "classe" ? (
                        <AddSeanceButton
                          creneauId={ligne.creneau.id}
                          jour={j}
                          classeId={selectedClasse}
                          matieres={matieres}
                          enseignants={enseignants}
                          onAdded={loadGrille}
                        />
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}

function AddSeanceButton({
  creneauId,
  jour,
  classeId,
  matieres,
  enseignants,
  onAdded,
}: {
  creneauId: string;
  jour: number;
  classeId: string;
  matieres: Matiere[];
  enseignants: PersonnelListItem[];
  onAdded: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [matiereId, setMatiereId] = useState(matieres[0]?.id ?? "");
  const [personnelId, setPersonnelId] = useState(enseignants[0]?.id ?? "");

  async function handleAdd() {
    const token = getToken();
    if (!token || !matiereId || !personnelId) return;
    try {
      await createSeance(token, {
        classe_id: classeId,
        creneau_id: creneauId,
        jour_semaine: jour,
        matiere_id: matiereId,
        personnel_id: personnelId,
      });
      setOpen(false);
      onAdded();
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Erreur");
    }
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="text-xs text-emerald-600 hover:underline"
      >
        + Ajouter
      </button>
    );
  }

  return (
    <div className="space-y-1 rounded border border-slate-200 p-2">
      <select value={matiereId} onChange={(e) => setMatiereId(e.target.value)} className="w-full rounded border px-1 py-0.5 text-xs">
        {matieres.map((m) => <option key={m.id} value={m.id}>{m.libelle}</option>)}
      </select>
      <select value={personnelId} onChange={(e) => setPersonnelId(e.target.value)} className="w-full rounded border px-1 py-0.5 text-xs">
        {enseignants.map((e) => <option key={e.id} value={e.id}>{e.prenoms} {e.nom}</option>)}
      </select>
      <div className="flex gap-1">
        <button type="button" onClick={handleAdd} className="text-xs text-emerald-700">OK</button>
        <button type="button" onClick={() => setOpen(false)} className="text-xs text-slate-500">Annuler</button>
      </div>
    </div>
  );
}
