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

function KpiSkeleton() {
  return (
    <div className="aw-kpi">
      <div className="aw-skeleton h-3.5 w-28" />
      <div className="aw-skeleton mt-4 h-10 w-24" />
      <div className="aw-skeleton mt-3 h-3 w-32" />
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
          value: kpi.taux_presence_mois != null ? `${kpi.taux_presence_mois} %` : "Non renseigné",
          hint: "Taux global",
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="aw-badge-tag">Vue d&apos;ensemble</span>
          <h2 className="mt-3 text-[40px] font-semibold leading-[1.28] text-obsidian">
            Indicateurs clés
          </h2>
          <p className="mt-2 text-[15px] text-steel">
            {kpi?.annee_libelle ?? "Chargement des données de l'année scolaire"}
          </p>
        </div>
        {canReports && (
          <Link href="/dashboard/rapports" className="aw-btn-primary inline-block">
            Voir les rapports
          </Link>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {loading && canReports
          ? Array.from({ length: 6 }).map((_, i) => <KpiSkeleton key={i} />)
          : cards.map((card) => (
              <div key={card.label} className="aw-kpi">
                <p className="text-[14px] text-steel">{card.label}</p>
                <p className="aw-kpi-value mt-2">{card.value}</p>
                <p className="mt-2 text-[12px] text-fog">{card.hint}</p>
              </div>
            ))}
      </div>

      <hr className="aw-divider" />

      <div className="aw-card">
        <h3 className="text-[28px] font-semibold leading-[1.28] text-obsidian">État des services</h3>
        <p className="mt-1 text-[14px] text-steel">Backend FastAPI et services associés</p>

        {error && (
          <div className="aw-error mt-4">
            {error}. Lancez <code className="font-mono text-[13px]">docker compose up -d</code> en local.
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
              <div key={i} className="aw-skeleton h-[52px]" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-[14px] border border-cloud bg-paper px-4 py-3">
      <dt className="text-[14px] text-steel">{label}</dt>
      <dd className={`text-[14px] font-medium capitalize ${ok ? "text-graphite" : "text-ember"}`}>
        {value}
      </dd>
    </div>
  );
}
