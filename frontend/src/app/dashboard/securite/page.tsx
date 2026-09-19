"use client";

import { useEffect, useState } from "react";
import {
  cloturerAnnee,
  getSauvegardeStatus,
  listAuditLogs,
  listConnexions,
  listHistoriqueNotes,
  listHistoriquePaiements,
} from "@/lib/api/securite";
import { listAnnees } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { AnneeScolaire } from "@/types/parametrage";
import type { AuditLog, HistoriqueNote, HistoriquePaiement, LoginLog, SauvegardeStatus } from "@/types/securite";

type Tab = "audit" | "notes" | "paiements" | "connexions" | "sauvegarde" | "archivage";

export default function SecuritePage() {
  const [tab, setTab] = useState<Tab>("audit");
  const [audit, setAudit] = useState<AuditLog[]>([]);
  const [histNotes, setHistNotes] = useState<HistoriqueNote[]>([]);
  const [histPaie, setHistPaie] = useState<HistoriquePaiement[]>([]);
  const [connexions, setConnexions] = useState<LoginLog[]>([]);
  const [sauvegarde, setSauvegarde] = useState<SauvegardeStatus | null>(null);
  const [annees, setAnnees] = useState<AnneeScolaire[]>([]);
  const [error, setError] = useState<string | null>(null);

  const canAudit = hasPermission("security.audit");
  const canManage = hasPermission("settings.manage");

  useEffect(() => {
    const token = getToken();
    if (!token || !canAudit) return;
    if (tab === "audit") listAuditLogs(token).then(setAudit);
    if (tab === "notes") listHistoriqueNotes(token).then(setHistNotes);
    if (tab === "paiements") listHistoriquePaiements(token).then(setHistPaie);
    if (tab === "connexions") listConnexions(token).then(setConnexions);
    if (tab === "sauvegarde") getSauvegardeStatus(token).then(setSauvegarde);
    if (tab === "archivage" && canManage) listAnnees(token).then(setAnnees);
  }, [tab, canAudit, canManage]);

  async function handleCloturer(anneeId: string) {
    const token = getToken();
    if (!token || !canManage) return;
    try {
      await cloturerAnnee(token, anneeId);
      const token2 = getToken();
      if (token2) setAnnees(await listAnnees(token2));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur clôture");
    }
  }

  if (!canAudit) {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Vous n&apos;avez pas accès à la sécurité et l&apos;audit.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Sécurité & audit</h2>
        <p className="mt-1 text-sm text-slate-600">Journal d&apos;audit, historiques et sauvegardes</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {(
          [
            ["audit", "Audit"],
            ["notes", "Historique notes"],
            ["paiements", "Historique paiements"],
            ["connexions", "Connexions"],
            ["sauvegarde", "Sauvegarde"],
            ...(canManage ? [["archivage", "Archivage"]] : []),
          ] as [Tab, string][]
        ).map(([t, label]) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t ? "bg-emerald-700 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "audit" && <AuditTable rows={audit} />}
      {tab === "notes" && <HistNotesTable rows={histNotes} />}
      {tab === "paiements" && <HistPaieTable rows={histPaie} />}
      {tab === "connexions" && <ConnexionsTable rows={connexions} />}

      {tab === "sauvegarde" && sauvegarde && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="font-semibold text-slate-900">État des sauvegardes</h3>
          <dl className="grid gap-3 sm:grid-cols-2 text-sm">
            <div><dt className="text-slate-500">Répertoire</dt><dd className="font-mono text-xs">{sauvegarde.repertoire}</dd></div>
            <div><dt className="text-slate-500">Dernière sauvegarde</dt><dd>{sauvegarde.derniere_sauvegarde ?? "Aucune"}</dd></div>
            <div><dt className="text-slate-500">Taille</dt><dd>{sauvegarde.taille_octets ? `${Math.round(sauvegarde.taille_octets / 1024)} Ko` : "—"}</dd></div>
            <div><dt className="text-slate-500">HTTPS requis (prod)</dt><dd>{sauvegarde.https_requis ? "Oui" : "Non (dev)"}</dd></div>
          </dl>
          <p className="text-sm text-slate-600">
            Procédure : <code className="rounded bg-slate-100 px-1">{sauvegarde.procedure_restauration}</code>
          </p>
          <p className="text-sm text-slate-600">{sauvegarde.chiffrement}</p>
          <code className="block rounded-lg bg-slate-900 p-3 text-xs text-emerald-300">
            .\scripts\backup-db.ps1
          </code>
        </div>
      )}

      {tab === "archivage" && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left">Année</th>
                <th className="px-4 py-3 text-left">Statut</th>
                <th className="px-4 py-3 text-left">Active</th>
                {canManage && <th className="px-4 py-3 text-left">Action</th>}
              </tr>
            </thead>
            <tbody>
              {annees.map((a) => (
                <tr key={a.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{a.libelle}</td>
                  <td className="px-4 py-2 capitalize">{a.statut}</td>
                  <td className="px-4 py-2">{a.is_active ? "Oui" : "Non"}</td>
                  {canManage && (
                    <td className="px-4 py-2">
                      {a.statut !== "cloturee" && !a.is_active && (
                        <button
                          type="button"
                          onClick={() => handleCloturer(a.id)}
                          className="text-amber-700 hover:underline"
                        >
                          Clôturer (lecture seule)
                        </button>
                      )}
                      {a.statut === "cloturee" && (
                        <span className="text-xs text-slate-500">Archivée</span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AuditTable({ rows }: { rows: AuditLog[] }) {
  return (
    <Table
      headers={["Date", "Utilisateur", "Action", "Ressource", "Détails", "IP"]}
      empty="Aucune entrée d'audit."
      rows={rows.map((r) => [
        r.created_at.slice(0, 19),
        r.user_email ?? "—",
        r.action,
        `${r.resource_type}${r.resource_id ? ` #${r.resource_id.slice(0, 8)}` : ""}`,
        r.details ?? "—",
        r.ip_address ?? "—",
      ])}
    />
  );
}

function HistNotesTable({ rows }: { rows: HistoriqueNote[] }) {
  return (
    <Table
      headers={["Date", "Élève", "Ancienne", "Nouvelle"]}
      empty="Aucun historique de notes."
      rows={rows.map((r) => [
        r.created_at.slice(0, 19),
        r.eleve_id.slice(0, 8),
        r.ancienne_valeur ?? "—",
        r.nouvelle_valeur ?? "—",
      ])}
    />
  );
}

function HistPaieTable({ rows }: { rows: HistoriquePaiement[] }) {
  return (
    <Table
      headers={["Date", "Action", "Montant", "Statut", "Détails"]}
      empty="Aucun historique de paiements."
      rows={rows.map((r) => [
        r.created_at.slice(0, 19),
        r.action,
        r.montant,
        r.statut_apres,
        r.details ?? "—",
      ])}
    />
  );
}

function ConnexionsTable({ rows }: { rows: LoginLog[] }) {
  return (
    <Table
      headers={["Date", "Email", "IP", "Succès"]}
      empty="Aucune connexion enregistrée."
      rows={rows.map((r) => [
        r.created_at.slice(0, 19),
        r.email,
        r.ip_address ?? "—",
        r.success ? "Oui" : "Non",
      ])}
    />
  );
}

function Table({ headers, rows, empty }: { headers: string[]; rows: string[][]; empty: string }) {
  if (rows.length === 0) return <p className="text-sm text-slate-500">{empty}</p>;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50">
          <tr>{headers.map((h) => <th key={h} className="px-4 py-3 text-left">{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100">
              {row.map((cell, j) => <td key={j} className="px-4 py-2">{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
