"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { getDashboardKPI } from "@/lib/api/rapports";
import { ApiError } from "@/lib/api/client";
import { ROLE_LABELS, getToken, getUser, hasPermission } from "@/lib/auth/session";
import { NAV_SECTIONS, filterVisibleNavItems } from "@/lib/navigation";
import { NavIcon } from "@/components/ui/NavIcon";
import type { DashboardKPI } from "@/types/rapports";

function fmt(n: number | string) {
  return `${Math.round(Number(n)).toLocaleString("fr-FR")} GNF`;
}

export default function DashboardPage() {
  const [kpi, setKpi] = useState<DashboardKPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const user = getUser();
  const canReports = hasPermission("reports.view") || hasPermission("reports.view_pedagogical");
  const showScolarite = hasPermission("students.view");
  const showFinance =
    hasPermission("payments.view") ||
    hasPermission("payments.collect") ||
    hasPermission("reports.view");
  const showPersonnel = hasPermission("personnel.view");
  const showPresence = hasPermission("attendance.view") || hasPermission("attendance.manage");

  const shortcuts = useMemo(
    () =>
      filterVisibleNavItems(
        NAV_SECTIONS.flatMap((section) => section.items),
        (p) => !p || hasPermission(p),
      ).filter((item) => item.href !== "/dashboard"),
    [],
  );

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getDashboardKPI(token)
      .then(setKpi)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger la synthèse"))
      .finally(() => setLoading(false));
  }, []);

  const summaryRows = useMemo(() => {
    if (!kpi) return [];
    const rows: { label: string; value: string }[] = [];
    if (showScolarite) {
      rows.push({ label: "Élèves inscrits", value: String(kpi.total_eleves) });
      rows.push({ label: "Classes", value: String(kpi.total_classes) });
    }
    if (showFinance) {
      rows.push({ label: "Recettes du mois", value: fmt(kpi.recettes_mois) });
      rows.push({
        label: "Impayés",
        value: `${fmt(kpi.total_impayes)} (${kpi.nombre_impayes} élève(s))`,
      });
    }
    if (showPersonnel) {
      rows.push({ label: "Personnel actif", value: String(kpi.total_personnel) });
    }
    if (showPresence) {
      rows.push({
        label: "Présence ce mois",
        value: kpi.taux_presence_mois != null ? `${kpi.taux_presence_mois} %` : "—",
      });
    }
    return rows;
  }, [kpi, showScolarite, showFinance, showPersonnel, showPresence]);

  const roleLabel = user ? (ROLE_LABELS[user.role] ?? user.role) : "";

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header>
        <h2 className="text-xl font-semibold text-slate-900">Tableau de bord</h2>
        {user && (
          <p className="mt-1 text-sm text-slate-600">
            {user.prenom} {user.nom}
            {roleLabel ? ` · ${roleLabel}` : ""}
          </p>
        )}
      </header>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
          <h3 className="text-sm font-semibold text-slate-900">Synthèse</h3>
          <p className="text-xs text-slate-500">
            {loading
              ? "Chargement…"
              : kpi?.annee_libelle
                ? `Année scolaire : ${kpi.annee_libelle}`
                : "Année scolaire non configurée"}
          </p>
        </div>

        {loading ? (
          <p className="px-4 py-6 text-sm text-slate-500">Chargement des chiffres…</p>
        ) : summaryRows.length === 0 ? (
          <p className="px-4 py-6 text-sm text-slate-500">
            Aucun indicateur disponible pour votre profil. Utilisez les raccourcis ci-dessous.
          </p>
        ) : (
          <dl className="divide-y divide-slate-100 sm:grid sm:grid-cols-2 sm:divide-y-0 lg:grid-cols-3">
            {summaryRows.map((row) => (
              <div
                key={row.label}
                className="flex items-baseline justify-between gap-4 px-4 py-3 sm:block sm:border-r sm:border-slate-100 last:sm:border-r-0"
              >
                <dt className="text-sm text-slate-600">{row.label}</dt>
                <dd className="text-base font-semibold tabular-nums text-slate-900">{row.value}</dd>
              </div>
            ))}
          </dl>
        )}

        {canReports && !loading && (
          <div className="border-t border-slate-200 px-4 py-3">
            <Link href="/dashboard/rapports" className="text-sm font-medium text-teal-700 hover:underline">
              Ouvrir les rapports détaillés
            </Link>
          </div>
        )}
      </section>

      {shortcuts.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold text-slate-900">Accès rapide</h3>
          <ul className="grid gap-2 sm:grid-cols-2">
            {shortcuts.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 hover:border-slate-300 hover:bg-slate-50"
                >
                  <NavIcon name={item.icon} className="h-4 w-4 shrink-0 text-slate-500" />
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
