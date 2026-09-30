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

const KPI_COLORS = [
  { gradient: "from-teal-500 to-teal-600", icon: "👨‍🎓" },
  { gradient: "from-blue-500 to-blue-600", icon: "🏫" },
  { gradient: "from-emerald-500 to-emerald-600", icon: "💰" },
  { gradient: "from-amber-500 to-amber-600", icon: "⚠️" },
  { gradient: "from-purple-500 to-purple-600", icon: "👥" },
  { gradient: "from-sky-500 to-sky-600", icon: "📊" },
];

function KpiSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="fd-skeleton h-4 w-28" />
      <div className="fd-skeleton mt-4 h-8 w-24" />
      <div className="fd-skeleton mt-3 h-3 w-32" />
    </div>
  );
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [kpi, setKpi] = useState<DashboardKPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const canReports = hasPermission("reports.view") || hasPermission("reports.view_pedagogical");

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setError("API indisponible"));
  }, []);

  useEffect(() => {
    const token = getToken();
    if (!token || !canReports) {
      setLoading(false);
      return;
    }
    setLoading(true);
    getDashboardKPI(token)
      .then(setKpi)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erreur KPI"))
      .finally(() => setLoading(false));
  }, [canReports]);

  const cards = kpi
    ? [
        { label: "Élèves inscrits", value: String(kpi.total_eleves), hint: kpi.annee_libelle },
        { label: "Classes actives", value: String(kpi.total_classes), hint: "Année en cours" },
        { label: "Recettes du mois", value: fmt(kpi.recettes_mois), hint: "Encaissements validés" },
        { label: "Impayés", value: fmt(kpi.total_impayes), hint: `${kpi.nombre_impayes} élève(s)` },
        { label: "Personnel actif", value: String(kpi.total_personnel), hint: "Enseignants et staff" },
        {
          label: "Présence (mois)",
          value: kpi.taux_presence_mois != null ? `${kpi.taux_presence_mois} %` : "N/A",
          hint: "Taux global",
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="inline-flex items-center rounded-lg bg-teal-50 px-3 py-1 text-[12px] font-semibold text-teal-700">
            Vue d&apos;ensemble
          </span>
          <h2 className="mt-3 text-[32px] font-bold leading-tight text-slate-900">
            Indicateurs clés
          </h2>
          <p className="mt-1 text-[15px] text-slate-500">
            {kpi?.annee_libelle ?? "Chargement des données de l'année scolaire…"}
          </p>
        </div>
        {canReports && (
          <Link
            href="/dashboard/rapports"
            className="inline-flex items-center gap-2 rounded-xl bg-teal-600 px-5 py-2.5 text-[14px] font-semibold text-white shadow-sm transition hover:bg-teal-700"
          >
            📈 Voir les rapports
          </Link>
        )}
      </div>

      {/* KPI grid */}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {loading && canReports
          ? Array.from({ length: 6 }).map((_, i) => <KpiSkeleton key={i} />)
          : cards.map((card, i) => {
              const color = KPI_COLORS[i % KPI_COLORS.length];
              return (
                <div key={card.label} className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md">
                  <div className={`absolute -right-4 -top-4 h-20 w-20 rounded-full bg-gradient-to-br ${color.gradient} opacity-10 transition group-hover:opacity-20`} />
                  <div className="relative">
                    <div className="flex items-center justify-between">
                      <p className="text-[14px] font-medium text-slate-500">{card.label}</p>
                      <span className="text-xl">{color.icon}</span>
                    </div>
                    <p className="mt-2 text-[28px] font-bold text-slate-900">{card.value}</p>
                    <p className="mt-1 text-[13px] text-slate-400">{card.hint}</p>
                  </div>
                </div>
              );
            })}
      </div>

      <hr className="border-slate-200" />

      {/* Health status */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
            <span className="text-lg">🖥️</span>
          </div>
          <div>
            <h3 className="text-[20px] font-bold text-slate-900">État des services</h3>
            <p className="text-[14px] text-slate-500">Backend FastAPI et services associés</p>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-[14px] text-red-700">
            {error}. Lancez <code className="rounded bg-red-100 px-1.5 py-0.5 font-mono text-[13px]">docker compose up -d</code> en local.
          </div>
        )}

        {health ? (
          <dl className="mt-5 grid gap-3 sm:grid-cols-2">
            <StatusItem label="API" value={health.status} ok={health.status === "ok"} />
            <StatusItem label="Environnement" value={health.environment} ok />
            <StatusItem label="PostgreSQL" value={health.database} ok={health.database === "ok"} />
            <StatusItem label="Redis" value={health.redis} ok={health.redis === "ok"} />
          </dl>
        ) : (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="fd-skeleton h-[52px]" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 transition hover:bg-slate-100">
      <dt className="text-[14px] font-medium text-slate-600">{label}</dt>
      <dd className={`flex items-center gap-2 text-[14px] font-semibold capitalize ${ok ? "text-emerald-600" : "text-red-500"}`}>
        <span className={`h-2 w-2 rounded-full ${ok ? "bg-emerald-500" : "bg-red-500"}`} />
        {value}
      </dd>
    </div>
  );
}
