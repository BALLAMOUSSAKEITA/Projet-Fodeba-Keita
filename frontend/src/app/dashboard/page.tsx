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
    <div className="ws-kpi">
      <div className="ws-skeleton h-3.5 w-28" />
      <div className="ws-skeleton mt-4 h-9 w-20" />
      <div className="ws-skeleton mt-3 h-3 w-32" />
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
          <p className="ws-link !normal-case !tracking-normal !text-[13px]">Vue d&apos;ensemble</p>
          <h2 className="mt-2 font-display text-[40px] font-light tracking-[-0.8px] text-canvas-white">
            Indicateurs clés
          </h2>
          <p className="mt-2 text-[16px] text-silver-mist">
            {kpi?.annee_libelle ?? "Chargement des données de l'année scolaire"}
          </p>
        </div>
        {canReports && (
          <Link href="/dashboard/rapports" className="ws-btn-primary inline-block">
            Voir les rapports
          </Link>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {loading && canReports
          ? Array.from({ length: 6 }).map((_, i) => <KpiSkeleton key={i} />)
          : cards.map((card) => (
              <div key={card.label} className="ws-kpi">
                <p className="text-[14px] text-silver-mist">{card.label}</p>
                <p className="mt-2 font-display text-[32px] font-light tracking-[-0.5px] text-canvas-white">
                  {card.value}
                </p>
                <p className="mt-2 text-[12px] text-bioluminescent-teal">{card.hint}</p>
              </div>
            ))}
      </div>

      <hr className="ws-divider" />

      <div className="ws-card">
        <h3 className="font-display text-[28px] font-light tracking-[-0.56px] text-canvas-white">
          État des services
        </h3>
        <p className="mt-1 text-[14px] text-silver-mist">Backend FastAPI et services associés</p>

        {error && (
          <div className="ws-error mt-4">
            {error}. Lancez <code className="font-mono">docker compose up -d</code> en local.
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
              <div key={i} className="ws-skeleton h-[52px]" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-silver-mist/20 bg-midnight-navy px-4 py-3">
      <dt className="text-[14px] text-silver-mist">{label}</dt>
      <dd className={`text-[14px] font-medium capitalize ${ok ? "text-bioluminescent-teal" : "text-bubblegum"}`}>
        {value}
      </dd>
    </div>
  );
}
