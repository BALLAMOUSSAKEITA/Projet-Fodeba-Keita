"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api/auth";
import { getDashboardKPI } from "@/lib/api/rapports";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { DashboardKPI } from "@/types/rapports";

interface HealthStatus {
  status: string;
  environment: string;
  database: string;
  redis: string;
}

function fmt(n: number | string) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [kpi, setKpi] = useState<DashboardKPI | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canReports = hasPermission("reports.view") || hasPermission("reports.view_pedagogical");

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setError("API indisponible"));
  }, []);

  useEffect(() => {
    const token = getToken();
    if (!token || !canReports) return;
    getDashboardKPI(token)
      .then(setKpi)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erreur KPI"));
  }, [canReports]);

  const cards = kpi
    ? [
        { label: "Élèves inscrits", value: String(kpi.total_eleves), hint: kpi.annee_libelle },
        { label: "Classes actives", value: String(kpi.total_classes), hint: "Année en cours" },
        { label: "Recettes du mois", value: fmt(kpi.recettes_mois), hint: "Encaissements validés" },
        { label: "Impayés", value: fmt(kpi.total_impayes), hint: `${kpi.nombre_impayes} élève(s)` },
        { label: "Personnel actif", value: String(kpi.total_personnel), hint: "Enseignants & staff" },
        {
          label: "Présence (mois)",
          value: kpi.taux_presence_mois != null ? `${kpi.taux_presence_mois} %` : "—",
          hint: "Taux global",
        },
      ]
    : [
        { label: "Élèves inscrits", value: "—", hint: "Chargement…" },
        { label: "Classes actives", value: "—", hint: "Chargement…" },
        { label: "Recettes du mois", value: "—", hint: "Chargement…" },
        { label: "Impayés", value: "—", hint: "Chargement…" },
      ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Tableau de bord</h2>
          <p className="mt-1 text-slate-600">
            Groupe Scolaire Privé Fodeba Keita — {kpi?.annee_libelle ?? "…"}
          </p>
        </div>
        {canReports && (
          <Link
            href="/dashboard/rapports"
            className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
          >
            Voir les rapports
          </Link>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-sm text-slate-500">{card.label}</p>
            <p className="mt-2 text-2xl font-bold text-slate-900">{card.value}</p>
            <p className="mt-1 text-xs text-emerald-600">{card.hint}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">État des services</h3>
        <p className="mt-1 text-sm text-slate-500">
          Vérification de la connexion avec le backend FastAPI
        </p>

        {error && (
          <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error} — Lancez <code className="font-mono">docker compose up -d</code>
          </div>
        )}

        {health && (
          <dl className="mt-4 grid gap-3 sm:grid-cols-2">
            <StatusItem label="API" value={health.status} ok={health.status === "ok"} />
            <StatusItem label="Environnement" value={health.environment} ok />
            <StatusItem label="PostgreSQL" value={health.database} ok={health.database === "ok"} />
            <StatusItem label="Redis" value={health.redis} ok={health.redis === "ok"} />
          </dl>
        )}
      </div>
    </div>
  );
}

function StatusItem({
  label,
  value,
  ok,
}: {
  label: string;
  value: string;
  ok: boolean;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3">
      <dt className="text-sm text-slate-600">{label}</dt>
      <dd
        className={`text-sm font-medium ${ok ? "text-emerald-700" : "text-amber-700"}`}
      >
        {value}
      </dd>
    </div>
  );
}
