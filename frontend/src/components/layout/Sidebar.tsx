"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/session";

type NavItem = {
  href: string;
  label: string;
  icon: string;
  permission?: string;
  disabled?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Tableau de bord", icon: "📊" },
  { href: "/dashboard/utilisateurs", label: "Utilisateurs", icon: "👤", permission: "users.manage" },
  { href: "/dashboard/roles", label: "Rôles", icon: "🔐", permission: "users.manage" },
  { href: "/dashboard/eleves", label: "Élèves", icon: "👨‍🎓", permission: "students.view" },
  { href: "/dashboard/classes", label: "Classes", icon: "🏫", permission: "students.view" },
  { href: "/dashboard/personnel", label: "Personnel", icon: "👩‍🏫", permission: "personnel.view" },
  { href: "/dashboard/emploi-du-temps", label: "Emploi du temps", icon: "📅", permission: "timetable.view" },
  { href: "/dashboard/notes", label: "Notes", icon: "📝", permission: "grades.modify" },
  { href: "/dashboard/bulletins", label: "Bulletins", icon: "📋", permission: "grades.validate_bulletins" },
  { href: "/dashboard/presences", label: "Présences", icon: "✅", permission: "attendance.view" },
  { href: "/dashboard/finance", label: "Finance", icon: "💰", permission: "payments.view" },
  { href: "/dashboard/paie", label: "Paie", icon: "💼", permission: "payroll.view" },
  { href: "/dashboard/comptabilite", label: "Comptabilité", icon: "📒", permission: "reports.view" },
  { href: "/dashboard/rapports", label: "Rapports", icon: "📈", permission: "reports.view" },
  { href: "/dashboard/securite", label: "Sécurité", icon: "🔒", permission: "security.audit" },
  { href: "/dashboard/annonces", label: "Annonces", icon: "📢", permission: "communication.view" },
  { href: "/dashboard/portail", label: "Portail parent", icon: "👨‍👩‍👧", permission: "parent.portal" },
  { href: "/dashboard/parametres", label: "Paramètres", icon: "⚙️", permission: "settings.view" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">
          SGEP
        </p>
        <h2 className="mt-1 text-sm font-bold leading-snug text-slate-900">
          Groupe Scolaire Privé
          <br />
          Fodeba Keita
        </h2>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {NAV_ITEMS.map((item) => {
          if (item.permission && !hasPermission(item.permission)) {
            return null;
          }

          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
          const className = [
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
            item.disabled
              ? "cursor-not-allowed text-slate-400"
              : isActive
                ? "bg-emerald-50 text-emerald-800"
                : "text-slate-700 hover:bg-slate-50",
          ].join(" ");

          if (item.disabled) {
            return (
              <span key={item.href} className={className} title="Bientôt disponible">
                <span>{item.icon}</span>
                {item.label}
              </span>
            );
          }

          return (
            <Link key={item.href} href={item.href} className={className}>
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 p-4 text-xs text-slate-500">
        Sprint 17 — Sécurité
      </div>
    </aside>
  );
}
