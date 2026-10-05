"use client";

import { useCallback, useEffect, useState } from "react";
import {
  annulerPaiement,
  createPaiement,
  createTarif,
  downloadRecuPdf,
  getCaisseJournaliere,
  getSituationEleve,
  listImpayes,
  listTarifs,
  relancerImpaye,
  updateTarif,
} from "@/lib/api/paiements";
import { getClasseEleves } from "@/lib/api/classes";
import { useAnneeScolaire } from "@/components/layout/AnneeScolaireProvider";
import { listClasses, listNiveaux, listTypesFrais } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Niveau } from "@/types/parametrage";
import type { CaisseJournaliere, ImpayeItem, Paiement, SituationEleve } from "@/types/paiements";
import type { Classe, TypeFrais } from "@/types/parametrage";
import { RecuPaiementCard } from "@/components/finance/RecuPaiementCard";

type Tab = "encaissement" | "impayes" | "caisse" | "scolarite";

const MODES = [
  { value: "especes", label: "Espèces" },
  { value: "orange_money", label: "Orange Money" },
  { value: "mtn_momo", label: "MTN MoMo" },
  { value: "virement", label: "Virement" },
  { value: "cheque", label: "Chèque" },
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function fmt(n: number) {
  return `${Math.round(n).toLocaleString("fr-FR")} GNF`;
}

export default function FinancePage() {
  const { anneeId, anneeLibelle } = useAnneeScolaire();
  const [tab, setTab] = useState<Tab>("encaissement");
  const [classes, setClasses] = useState<Classe[]>([]);
  const [typesFrais, setTypesFrais] = useState<TypeFrais[]>([]);
  const [classeId, setClasseId] = useState("");
  const [eleveId, setEleveId] = useState("");
  const [eleves, setEleves] = useState<{ id: string; nom: string; prenoms: string; matricule: string }[]>([]);
  const [montant, setMontant] = useState("");
  const [situation, setSituation] = useState<SituationEleve | null>(null);
  const [lastPaiement, setLastPaiement] = useState<Paiement | null>(null);
  const [impayes, setImpayes] = useState<ImpayeItem[]>([]);
  const [caisse, setCaisse] = useState<CaisseJournaliere | null>(null);
  const [caisseDate, setCaisseDate] = useState(todayIso());
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [tarifByNiveau, setTarifByNiveau] = useState<Record<string, { tarifId: string; montant: string }>>({});
  const [montantDraft, setMontantDraft] = useState<Record<string, string>>({});
  const [loadingTarifs, setLoadingTarifs] = useState(false);
  const [savingNiveauId, setSavingNiveauId] = useState<string | null>(null);
  const [downloadingRecuId, setDownloadingRecuId] = useState<string | null>(null);

  const canCollect = hasPermission("payments.collect");
  const canView = canCollect || hasPermission("payments.view");
  const canCancel = canCollect;

  useEffect(() => {
    const token = getToken();
    if (!token || !anneeId) return;
    Promise.all([listClasses(token, anneeId), listTypesFrais(token), listNiveaux(token)]).then(([c, tf, n]) => {
      setClasses(c);
      setTypesFrais(tf);
      setNiveaux(n);
      if (c.length) setClasseId(c[0].id);
    });
  }, [anneeId]);

  const loadTarifsScolarite = useCallback(async () => {
    const token = getToken();
    if (!token || !anneeId) return;
    setLoadingTarifs(true);
    setError(null);
    try {
      const all = await listTarifs(token, anneeId);
      const scol = all.filter((t) => t.type_frais_code === "SCOLARITE");
      const byNiveau: Record<string, { tarifId: string; montant: string }> = {};
      const draft: Record<string, string> = {};
      for (const t of scol) {
        byNiveau[t.niveau_id] = { tarifId: t.id, montant: String(t.montant) };
        draft[t.niveau_id] = String(Math.round(Number(t.montant)));
      }
      setTarifByNiveau(byNiveau);
      const draftAll: Record<string, string> = {};
      for (const n of niveaux) {
        draftAll[n.id] = byNiveau[n.id]?.montant ?? "";
      }
      setMontantDraft(draftAll);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de charger les tarifs");
    } finally {
      setLoadingTarifs(false);
    }
  }, [anneeId, niveaux]);

  useEffect(() => {
    if (tab === "scolarite" && niveaux.length > 0) {
      loadTarifsScolarite();
    }
  }, [tab, niveaux, loadTarifsScolarite]);

  useEffect(() => {
    const token = getToken();
    if (!token || !classeId) return;
    getClasseEleves(token, classeId).then((d) => {
      setEleves(d.eleves.map((e) => ({ id: e.id, nom: e.nom, prenoms: e.prenoms, matricule: e.matricule })));
      if (d.eleves.length) setEleveId(d.eleves[0].id);
    });
  }, [classeId]);

  useEffect(() => {
    const token = getToken();
    if (!token || !eleveId) return;
    getSituationEleve(token, eleveId).then(setSituation).catch(() => setSituation(null));
  }, [eleveId, lastPaiement]);

  const loadImpayes = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      setImpayes(await listImpayes(token, classeId || undefined));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [classeId]);

  const loadCaisse = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      setCaisse(await getCaisseJournaliere(token, caisseDate));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    }
  }, [caisseDate]);

  useEffect(() => {
    if (tab === "impayes") loadImpayes();
    if (tab === "caisse") loadCaisse();
  }, [tab, loadImpayes, loadCaisse]);

  async function handleEncaisser(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !canCollect) return;
    setSaving(true);
    setError(null);
    try {
      const scolariteType = typesFrais.find((t) => t.code === "SCOLARITE");
      if (!scolariteType) {
        setError("Type de frais « Scolarité » introuvable.");
        return;
      }
      const p = await createPaiement(token, {
        eleve_id: eleveId,
        type_frais_id: scolariteType.id,
        montant: Number(montant),
        mode_paiement: "especes",
      });
      setLastPaiement(p);
      setMontant("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur encaissement");
    } finally {
      setSaving(false);
    }
  }

  async function handleDownloadRecu(paiement: Paiement) {
    const token = getToken();
    if (!token) return;
    setDownloadingRecuId(paiement.id);
    setError(null);
    try {
      await downloadRecuPdf(token, paiement.id, `${paiement.numero_recu}.pdf`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur PDF");
    } finally {
      setDownloadingRecuId(null);
    }
  }

  async function handleSaveTarifNiveau(niveauId: string) {
    const token = getToken();
    if (!token || !canCollect || !anneeId) return;
    const raw = montantDraft[niveauId]?.trim();
    if (!raw) {
      setError("Indiquez un montant pour ce niveau.");
      return;
    }
    const montant = Number(raw);
    if (!Number.isFinite(montant) || montant < 0) {
      setError("Montant invalide.");
      return;
    }
    const scolariteType = typesFrais.find((t) => t.code === "SCOLARITE");
    if (!scolariteType) {
      setError("Type de frais « Scolarité » introuvable.");
      return;
    }
    setSavingNiveauId(niveauId);
    setError(null);
    try {
      const existing = tarifByNiveau[niveauId];
      if (existing?.tarifId) {
        await updateTarif(token, existing.tarifId, montant);
      } else {
        await createTarif(token, {
          annee_scolaire_id: anneeId,
          niveau_id: niveauId,
          type_frais_id: scolariteType.id,
          montant,
        });
      }
      await loadTarifsScolarite();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur enregistrement tarif");
    } finally {
      setSavingNiveauId(null);
    }
  }

  async function handleRelance(eleveIdRelance: string) {
    const token = getToken();
    if (!token) return;
    try {
      await relancerImpaye(token, {
        eleve_id: eleveIdRelance,
        canal: "appel",
        message: "Relance pour impayés scolarité",
      });
      await loadImpayes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur relance");
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès à la finance.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Finance — Paiements</h2>
        <p className="mt-1 text-sm text-slate-600">Encaissement, impayés et caisse journalière</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(["encaissement", "impayes", "caisse", "scolarite"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "encaissement"
              ? "Encaissement"
              : t === "impayes"
                ? "Impayés"
                : t === "caisse"
                  ? "Caisse"
                  : "Scolarité"}
          </button>
        ))}
      </div>

      {tab === "encaissement" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <form onSubmit={handleEncaisser} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900">Nouvel encaissement</h3>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Classe</span>
              <select
                value={classeId}
                onChange={(e) => setClasseId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nom}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Élève</span>
              <select
                required
                value={eleveId}
                onChange={(e) => setEleveId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {eleves.map((el) => (
                  <option key={el.id} value={el.id}>
                    {el.prenoms} {el.nom} ({el.matricule})
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-medium text-slate-700">Montant payé (GNF)</span>
              <input
                type="number"
                required
                min={1}
                value={montant}
                onChange={(e) => setMontant(e.target.value)}
                placeholder="Ex. 500000"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            {canCollect && (
              <button
                type="submit"
                disabled={saving}
                className="w-full rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
              >
                {saving ? "Encaissement…" : "Encaisser"}
              </button>
            )}
          </form>

          <div className="space-y-4">
            {situation && (
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900">Situation — {situation.prenoms} {situation.nom}</h3>
                <p className="mt-2 text-sm text-slate-600">{situation.annee_libelle}</p>
                <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">Dû</p>
                    <p className="font-bold text-slate-900">{fmt(Number(situation.total_du))}</p>
                  </div>
                  <div className="rounded-lg bg-emerald-50 p-3">
                    <p className="text-xs text-emerald-700">Payé</p>
                    <p className="font-bold text-emerald-800">{fmt(Number(situation.total_paye))}</p>
                  </div>
                  <div className="rounded-lg bg-red-50 p-3">
                    <p className="text-xs text-red-700">Reste</p>
                    <p className="font-bold text-red-800">{fmt(Number(situation.total_restant))}</p>
                  </div>
                </div>
              </div>
            )}

            {lastPaiement && (
              <div>
                <p className="mb-3 text-sm font-medium text-emerald-800">Paiement enregistré — reçu disponible</p>
                <RecuPaiementCard
                  paiement={lastPaiement}
                  anneeLibelle={anneeLibelle}
                  classeNom={classes.find((c) => c.id === classeId)?.nom}
                  resteApresPaiement={situation ? Number(situation.total_restant) : null}
                  onDownloadPdf={() => handleDownloadRecu(lastPaiement)}
                  downloading={downloadingRecuId === lastPaiement.id}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "impayes" && (
        <div className="table-responsive rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap gap-3 border-b border-slate-100 px-4 py-3">
            <select
              value={classeId}
              onChange={(e) => setClasseId(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Toutes les classes</option>
              {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
            </select>
          </div>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Élève</th>
                <th className="px-4 py-3 text-left">Classe</th>
                <th className="px-4 py-3 text-left">Reste</th>
                <th className="px-4 py-3 text-left">Retards</th>
                {canCollect && <th className="px-4 py-3 text-left" />}
              </tr>
            </thead>
            <tbody>
              {impayes.map((i) => (
                <tr key={i.eleve_id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{i.prenoms} {i.nom}</td>
                  <td className="px-4 py-2">{i.classe_nom ?? "—"}</td>
                  <td className="px-4 py-2 font-semibold text-red-700">{fmt(Number(i.montant_restant))}</td>
                  <td className="px-4 py-2">{i.tranches_en_retard}</td>
                  {canCollect && (
                    <td className="px-4 py-2">
                      <button
                        type="button"
                        onClick={() => handleRelance(i.eleve_id)}
                        className="text-emerald-700 hover:underline"
                      >
                        Relancer
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {impayes.length === 0 && (
            <p className="px-4 py-6 text-sm text-slate-500">Aucun impayé.</p>
          )}
        </div>
      )}

      {tab === "scolarite" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="font-semibold text-slate-900">Montants de scolarité par niveau</h3>
            <p className="mt-1 text-sm text-slate-600">
              Année scolaire : <span className="font-medium">{anneeLibelle || "—"}</span>
              {!canCollect && " (lecture seule)"}
            </p>
          </div>
          {loadingTarifs ? (
            <p className="text-sm text-slate-500">Chargement des tarifs…</p>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-4 py-3 font-medium">Niveau</th>
                    <th className="px-4 py-3 font-medium">Montant annuel (GNF)</th>
                    {canCollect && <th className="px-4 py-3 font-medium"></th>}
                  </tr>
                </thead>
                <tbody>
                  {niveaux.length === 0 ? (
                    <tr>
                      <td colSpan={canCollect ? 3 : 2} className="px-4 py-6 text-center text-slate-500">
                        Aucun niveau configuré
                      </td>
                    </tr>
                  ) : (
                    niveaux.map((n) => (
                      <tr key={n.id} className="border-t border-slate-100">
                        <td className="px-4 py-3 font-medium text-slate-900">
                          {n.libelle}
                          <span className="ml-2 font-mono text-xs text-slate-400">{n.code}</span>
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            min={0}
                            step={1000}
                            disabled={!canCollect}
                            value={montantDraft[n.id] ?? ""}
                            onChange={(e) =>
                              setMontantDraft((d) => ({ ...d, [n.id]: e.target.value }))
                            }
                            placeholder="Ex. 2500000"
                            className="w-full max-w-xs rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
                          />
                          {tarifByNiveau[n.id] && (
                            <p className="mt-1 text-xs text-slate-500">
                              Enregistré : {fmt(Number(tarifByNiveau[n.id].montant))}
                            </p>
                          )}
                        </td>
                        {canCollect && (
                          <td className="px-4 py-3">
                            <button
                              type="button"
                              disabled={savingNiveauId === n.id}
                              onClick={() => handleSaveTarifNiveau(n.id)}
                              className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50"
                            >
                              {savingNiveauId === n.id ? "…" : tarifByNiveau[n.id] ? "Mettre à jour" : "Enregistrer"}
                            </button>
                          </td>
                        )}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "caisse" && (
        <div className="space-y-4">
          <input
            type="date"
            value={caisseDate}
            onChange={(e) => setCaisseDate(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          {caisse && (
            <>
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <p className="text-xs text-slate-500">Total encaissé</p>
                  <p className="text-xl font-bold text-emerald-700">{fmt(Number(caisse.total_encaisse))}</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <p className="text-xs text-slate-500">Opérations</p>
                  <p className="text-xl font-bold text-slate-900">{caisse.nombre_paiements}</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <p className="text-xs text-slate-500">Par mode</p>
                  <ul className="mt-1 text-sm">
                    {Object.entries(caisse.par_mode).map(([m, v]) => (
                      <li key={m}>{MODES.find((x) => x.value === m)?.label ?? m} : {fmt(Number(v))}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="table-responsive rounded-xl border border-slate-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left">Reçu</th>
                      <th className="px-4 py-3 text-left">Élève</th>
                      <th className="px-4 py-3 text-left">Objet</th>
                      <th className="px-4 py-3 text-left">Montant</th>
                      <th className="px-4 py-3 text-left">Mode</th>
                      <th className="px-4 py-3 text-left">Reçu</th>
                      {canCancel && <th className="px-4 py-3 text-left"></th>}
                    </tr>
                  </thead>
                  <tbody>
                    {caisse.paiements.map((p) => (
                      <tr key={p.id} className="border-t border-slate-100">
                        <td className="px-4 py-2 font-mono text-xs">{p.numero_recu}</td>
                        <td className="px-4 py-2">{p.eleve_prenoms} {p.eleve_nom}</td>
                        <td className="px-4 py-2">{p.type_frais_libelle}</td>
                        <td className="px-4 py-2">{fmt(Number(p.montant))}</td>
                        <td className="px-4 py-2">{MODES.find((m) => m.value === p.mode_paiement)?.label ?? p.mode_paiement}</td>
                        <td className="px-4 py-2">
                          {p.statut === "valide" && (
                            <button
                              type="button"
                              className="text-sm font-medium text-emerald-700 hover:underline disabled:opacity-50"
                              disabled={downloadingRecuId === p.id}
                              onClick={() => handleDownloadRecu(p)}
                            >
                              {downloadingRecuId === p.id ? "…" : "PDF"}
                            </button>
                          )}
                        </td>
                        {canCancel && (
                          <td className="px-4 py-2">
                            {p.statut === "valide" && (
                              <button
                                type="button"
                                className="text-sm text-red-600 hover:underline"
                                onClick={async () => {
                                  const token = getToken();
                                  if (!token) return;
                                  const motif = window.prompt("Motif d'annulation ?");
                                  if (!motif) return;
                                  try {
                                    await annulerPaiement(token, p.id, motif);
                                    const refreshed = await getCaisseJournaliere(token, caisseDate);
                                    setCaisse(refreshed);
                                  } catch (err) {
                                    setError(err instanceof ApiError ? err.message : "Erreur annulation");
                                  }
                                }}
                              >
                                Annuler
                              </button>
                            )}
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
