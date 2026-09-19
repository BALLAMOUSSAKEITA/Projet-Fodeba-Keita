"use client";

import { useCallback, useEffect, useState } from "react";
import {
  archiverAnnonce,
  createAnnonce,
  envoyerMessage,
  listAnnonces,
  listHistoriqueCommunications,
  listModelesMessages,
  publierAnnonce,
} from "@/lib/api/communication";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Annonce, HistoriqueCommunication, ModeleMessage } from "@/types/communication";

type Tab = "annonces" | "envoi" | "historique";

const AUDIENCES = [
  { value: "tous", label: "Tous" },
  { value: "parents", label: "Parents" },
  { value: "personnel", label: "Personnel" },
];

const CANAUX = [
  { value: "sms", label: "SMS" },
  { value: "email", label: "Email" },
  { value: "app", label: "Application" },
  { value: "interne", label: "Interne" },
];

export default function AnnoncesPage() {
  const [tab, setTab] = useState<Tab>("annonces");
  const [annonces, setAnnonces] = useState<Annonce[]>([]);
  const [modeles, setModeles] = useState<ModeleMessage[]>([]);
  const [historique, setHistorique] = useState<HistoriqueCommunication[]>([]);
  const [form, setForm] = useState({ titre: "", contenu: "", audience: "tous" });
  const [envoi, setEnvoi] = useState({
    modele_id: "",
    canal: "sms",
    destinataire: "",
    sujet: "",
    corps: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canManage = hasPermission("communication.manage");
  const canView = canManage || hasPermission("communication.view");

  const loadAnnonces = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setAnnonces(await listAnnonces(token));
  }, []);

  useEffect(() => {
    if (!canView) return;
    loadAnnonces();
    const token = getToken();
    if (!token) return;
    listModelesMessages(token).then(setModeles);
  }, [canView, loadAnnonces]);

  useEffect(() => {
    const token = getToken();
    if (!token || tab !== "historique") return;
    listHistoriqueCommunications(token).then(setHistorique);
  }, [tab]);

  async function handleCreate(publier: boolean) {
    const token = getToken();
    if (!token || !canManage) return;
    setSaving(true);
    setError(null);
    try {
      await createAnnonce(token, form, publier);
      setForm({ titre: "", contenu: "", audience: "tous" });
      await loadAnnonces();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublier(id: string) {
    const token = getToken();
    if (!token) return;
    await publierAnnonce(token, id);
    await loadAnnonces();
  }

  async function handleArchiver(id: string) {
    const token = getToken();
    if (!token) return;
    await archiverAnnonce(token, id);
    await loadAnnonces();
  }

  async function handleEnvoi(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !canManage) return;
    setSaving(true);
    try {
      await envoyerMessage(token, {
        ...envoi,
        modele_id: envoi.modele_id || undefined,
      });
      setEnvoi({ modele_id: "", canal: "sms", destinataire: "", sujet: "", corps: "" });
      setTab("historique");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur envoi");
    } finally {
      setSaving(false);
    }
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès aux annonces.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Communication</h2>
        <p className="mt-1 text-sm text-slate-600">Annonces, modèles de messages et historique</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(["annonces", "envoi", "historique"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {t === "annonces" ? "Annonces" : t === "envoi" ? "Envoi" : "Historique"}
          </button>
        ))}
      </div>

      {tab === "annonces" && (
        <div className="grid gap-6 lg:grid-cols-2">
          {canManage && (
            <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Nouvelle annonce</h3>
              <input
                value={form.titre}
                onChange={(e) => setForm({ ...form, titre: e.target.value })}
                placeholder="Titre"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <textarea
                value={form.contenu}
                onChange={(e) => setForm({ ...form, contenu: e.target.value })}
                placeholder="Contenu"
                rows={4}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <select
                value={form.audience}
                onChange={(e) => setForm({ ...form, audience: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {AUDIENCES.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={saving}
                  onClick={() => handleCreate(false)}
                  className="flex-1 rounded-lg border border-slate-300 py-2 text-sm hover:bg-slate-50"
                >
                  Brouillon
                </button>
                <button
                  type="button"
                  disabled={saving}
                  onClick={() => handleCreate(true)}
                  className="flex-1 rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
                >
                  Publier
                </button>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {annonces.map((a) => (
              <div key={a.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold text-slate-900">{a.titre}</h4>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs capitalize">{a.statut}</span>
                </div>
                <p className="mt-2 text-sm text-slate-600 whitespace-pre-wrap">{a.contenu}</p>
                <p className="mt-2 text-xs text-slate-500">
                  {a.audience} · {a.date_publication ?? "—"} {a.auteur_nom ? `· ${a.auteur_nom}` : ""}
                </p>
                {canManage && a.statut === "brouillon" && (
                  <button
                    type="button"
                    onClick={() => handlePublier(a.id)}
                    className="mt-2 text-sm text-emerald-700 hover:underline"
                  >
                    Publier
                  </button>
                )}
                {canManage && a.statut === "publiee" && (
                  <button
                    type="button"
                    onClick={() => handleArchiver(a.id)}
                    className="mt-2 text-sm text-slate-500 hover:underline"
                  >
                    Archiver
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "envoi" && canManage && (
        <form onSubmit={handleEnvoi} className="max-w-lg space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="font-semibold text-slate-900">Envoyer un message (simulation)</h3>
          <select
            value={envoi.modele_id}
            onChange={(e) => {
              const m = modeles.find((x) => x.id === e.target.value);
              setEnvoi({
                ...envoi,
                modele_id: e.target.value,
                sujet: m?.sujet ?? envoi.sujet,
                corps: m?.corps ?? envoi.corps,
                canal: m?.canal ?? envoi.canal,
              });
            }}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">— Sans modèle —</option>
            {modeles.map((m) => (
              <option key={m.id} value={m.id}>{m.libelle}</option>
            ))}
          </select>
          <select
            value={envoi.canal}
            onChange={(e) => setEnvoi({ ...envoi, canal: e.target.value })}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {CANAUX.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
          <input
            required
            value={envoi.destinataire}
            onChange={(e) => setEnvoi({ ...envoi, destinataire: e.target.value })}
            placeholder="Destinataire (téléphone ou email)"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            required
            value={envoi.sujet}
            onChange={(e) => setEnvoi({ ...envoi, sujet: e.target.value })}
            placeholder="Sujet"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <textarea
            required
            value={envoi.corps}
            onChange={(e) => setEnvoi({ ...envoi, corps: e.target.value })}
            rows={4}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            {saving ? "Envoi…" : "Enregistrer dans l'historique"}
          </button>
        </form>
      )}

      {tab === "historique" && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Canal</th>
                <th className="px-4 py-3 text-left">Destinataire</th>
                <th className="px-4 py-3 text-left">Sujet</th>
                <th className="px-4 py-3 text-left">Statut</th>
                <th className="px-4 py-3 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {historique.map((h) => (
                <tr key={h.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 uppercase">{h.canal}</td>
                  <td className="px-4 py-2">{h.destinataire}</td>
                  <td className="px-4 py-2">{h.sujet}</td>
                  <td className="px-4 py-2 capitalize">{h.statut}</td>
                  <td className="px-4 py-2">{h.envoye_le?.slice(0, 10) ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
