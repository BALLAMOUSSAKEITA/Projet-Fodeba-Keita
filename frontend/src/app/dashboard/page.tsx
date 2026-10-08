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

  const statCards = useMemo(() => {
    if (!kpi) return [];
    const cards: { label: string; value: string }[] = [];
    if (showScolarite) {
      cards.push({ label: "Élèves inscrits", value: String(kpi.total_eleves) });
      cards.push({ label: "Classes", value: String(kpi.total_classes) });
    }
    if (showFinance) {
      cards.push({ label: "Recettes du mois", value: fmt(kpi.recettes_mois) });
      cards.push({ label: "Impayés", value: fmt(kpi.total_impayes) });
      cards.push({ label: "Élèves en impayé", value: String(kpi.nombre_impayes) });
    }
    if (showPersonnel) {
      cards.push({ label: "Personnel actif", value: String(kpi.total_personnel) });
    }
    return cards;
  }, [kpi, showScolarite, showFinance, showPersonnel]);

  const roleLabel = user ? (ROLE_LABELS[user.role] ?? user.role) : "";
  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return "Bonjour";
    if (h < 18) return "Bon après-midi";
    return "Bonsoir";
  })();

  return (
    <div className="space-y-8">
      <div className="fd-welcome-banner relative">
        <div className="relative z-[1]">
          <p className="text-sm font-medium text-teal-100/90">{greeting}</p>
          <h2 className="mt-1 text-xl font-bold text-white sm:text-2xl">
            {user ? `${user.prenom} ${user.nom}` : "Tableau de bord"}
          </h2>
          {roleLabel && <p className="mt-1 text-sm text-teal-50/80">{roleLabel}</p>}
          {!loading && kpi?.annee_libelle && (
            <p className="mt-3 inline-block rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
              Année scolaire {kpi.annee_libelle}
            </p>
          )}
        </div>
      </div>

      {error && (
        <div className="aw-error" role="alert">
          {error}
        </div>
      )}

      <section>
        <div className="mb-3 flex items-end justify-between gap-2">
          <h3 className="text-sm font-semibold text-slate-900">Indicateurs clés</h3>
          {canReports && !loading && (
            <Link href="/dashboard/rapports" className="aw-link text-sm">
              Rapports détaillés →
            </Link>
          )}
        </div>

        {loading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="fd-stat-card">
                <div className="aw-skeleton mb-2 h-4 w-24" />
                <div className="aw-skeleton h-8 w-32" />
              </div>
            ))}
          </div>
        ) : statCards.length === 0 ? (
          <div className="fd-panel px-4 py-8 text-center text-sm text-slate-500">
            Aucun indicateur pour votre profil. Utilisez les accès rapides ci-dessous.
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {statCards.map((card) => (
              <div key={card.label} className="fd-stat-card">
                <p className="fd-stat-label">{card.label}</p>
                <p className="fd-stat-value">{card.value}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {shortcuts.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold text-slate-900">Accès rapide</h3>
          <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {shortcuts.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="fd-shortcut-link">
                  <span className="fd-shortcut-icon">
                    <NavIcon name={item.icon} className="h-4 w-4" />
                  </span>
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
