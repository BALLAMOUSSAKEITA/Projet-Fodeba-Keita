"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createPaiement,
  downloadRecuPdf,
  getCaisseJournaliere,
  getSituationEleve,
  listImpayes,
  listTranches,
  relancerImpaye,
} from "@/lib/api/paiements";
import { getClasseEleves } from "@/lib/api/classes";
import { getAnneeActive, listClasses, listTypesFrais } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { CaisseJournaliere, ImpayeItem, Paiement, SituationEleve } from "@/types/paiements";
import type { Classe, TypeFrais } from "@/types/parametrage";

type Tab = "encaissement" | "impayes" | "caisse";

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
  const [tab, setTab] = useState<Tab>("encaissement");
  const [classes, setClasses] = useState<Classe[]>([]);
  const [typesFrais, setTypesFrais] = useState<TypeFrais[]>([]);
  const [classeId, setClasseId] = useState("");
  const [eleveId, setEleveId] = useState("");
  const [eleves, setEleves] = useState<{ id: string; nom: string; prenoms: string; matricule: string }[]>([]);
  const [typeFraisId, setTypeFraisId] = useState("");
  const [trancheId, setTrancheId] = useState("");
  const [tranches, setTranches] = useState<{ id: string; libelle: string }[]>([]);
  const [montant, setMontant] = useState("");
  const [mode, setMode] = useState("especes");
  const [reference, setReference] = useState("");
  const [situation, setSituation] = useState<SituationEleve | null>(null);
  const [lastPaiement, setLastPaiement] = useState<Paiement | null>(null);
  const [impayes, setImpayes] = useState<ImpayeItem[]>([]);
  const [caisse, setCaisse] = useState<CaisseJournaliere | null>(null);
  const [caisseDate, setCaisseDate] = useState(todayIso());
  const [anneeId, setAnneeId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canCollect = hasPermission("payments.collect");
  const canView = canCollect || hasPermission("payments.view");

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    getAnneeActive(token).then((a) => {
      setAnneeId(a.id);
      Promise.all([listClasses(token, a.id), listTypesFrais(token)]).then(([c, tf]) => {
        setClasses(c);
        setTypesFrais(tf);
        if (c.length) setClasseId(c[0].id);
        const scol = tf.find((t) => t.code === "SCOLARITE") ?? tf[0];
        if (scol) setTypeFraisId(scol.id);
      });
    });
  }, []);

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

  useEffect(() => {
    const token = getToken();
    if (!token || !anneeId || !typeFraisId) return;
    listTranches(token, anneeId, typeFraisId).then((t) => {
      setTranches(t);
      setTrancheId(t[0]?.id ?? "");
    });
  }, [anneeId, typeFraisId]);

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
      const p = await createPaiement(token, {
        eleve_id: eleveId,
        type_frais_id: typeFraisId,
        tranche_id: trancheId || undefined,
        montant: Number(montant),
        mode_paiement: mode,
        reference_externe: reference || undefined,
      });
      setLastPaiement(p);
      setMontant("");
      setReference("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur encaissement");
    } finally {
      setSaving(false);
    }
  }

  async function handleDownloadRecu() {
    const token = getToken();
    if (!token || !lastPaiement) return;
    try {
      await downloadRecuPdf(token, lastPaiement.id, `${lastPaiement.numero_recu}.pdf`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur PDF");
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
        {(["encaissement", "impayes", "caisse"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "encaissement" ? "Encaissement" : t === "impayes" ? "Impayés" : "Caisse"}
          </button>
        ))}
      </div>

      {tab === "encaissement" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <form onSubmit={handleEncaisser} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900">Nouvel encaissement</h3>
            <select
              value={classeId}
              onChange={(e) => setClasseId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
            </select>
            <select
              required
              value={eleveId}
              onChange={(e) => setEleveId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {eleves.map((el) => (
                <option key={el.id} value={el.id}>{el.prenoms} {el.nom} ({el.matricule})</option>
              ))}
            </select>
            <select
              value={typeFraisId}
              onChange={(e) => setTypeFraisId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {typesFrais.map((t) => <option key={t.id} value={t.id}>{t.libelle}</option>)}
            </select>
            {tranches.length > 0 && (
              <select
                value={trancheId}
                onChange={(e) => setTrancheId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">— Sans tranche —</option>
                {tranches.map((t) => <option key={t.id} value={t.id}>{t.libelle}</option>)}
              </select>
            )}
            <input
              type="number"
              required
              min={1}
              value={montant}
              onChange={(e) => setMontant(e.target.value)}
              placeholder="Montant (GNF)"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {MODES.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
            {(mode === "orange_money" || mode === "mtn_momo") && (
              <input
                type="text"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="Référence transaction"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            )}
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
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6">
                <p className="font-semibold text-emerald-900">Paiement enregistré</p>
                <p className="mt-1 text-sm text-emerald-800">Reçu {lastPaiement.numero_recu} — {fmt(Number(lastPaiement.montant))}</p>
                <button
                  type="button"
                  onClick={handleDownloadRecu}
                  className="mt-3 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
                >
                  Imprimer le reçu PDF
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "impayes" && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
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
              <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left">Reçu</th>
                      <th className="px-4 py-3 text-left">Élève</th>
                      <th className="px-4 py-3 text-left">Objet</th>
                      <th className="px-4 py-3 text-left">Montant</th>
                      <th className="px-4 py-3 text-left">Mode</th>
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
