export type NavIconName =
  | "dashboard"
  | "users"
  | "roles"
  | "students"
  | "classes"
  | "staff"
  | "calendar"
  | "grades"
  | "reports-card"
  | "attendance"
  | "finance"
  | "payroll"
  | "ledger"
  | "analytics"
  | "security"
  | "announcements"
  | "portal"
  | "settings";

export type NavItem = {
  href: string;
  label: string;
  icon: NavIconName;
  permission?: string;
};

export type NavSection = {
  title: string;
  items: NavItem[];
};

export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Vue d'ensemble",
    items: [{ href: "/dashboard", label: "Tableau de bord", icon: "dashboard" }],
  },
  {
    title: "Scolarité",
    items: [
      { href: "/dashboard/eleves", label: "Élèves", icon: "students", permission: "students.view" },
      { href: "/dashboard/classes", label: "Classes", icon: "classes", permission: "students.view" },
      { href: "/dashboard/notes", label: "Notes", icon: "grades", permission: "grades.modify" },
      {
        href: "/dashboard/bulletins",
        label: "Bulletins",
        icon: "reports-card",
        permission: "grades.validate_bulletins",
      },
      { href: "/dashboard/presences", label: "Présences", icon: "attendance", permission: "attendance.view" },
      {
        href: "/dashboard/emploi-du-temps",
        label: "Emploi du temps",
        icon: "calendar",
        permission: "timetable.view",
      },
    ],
  },
  {
    title: "Administration",
    items: [
      { href: "/dashboard/utilisateurs", label: "Utilisateurs", icon: "users", permission: "users.manage" },
      { href: "/dashboard/roles", label: "Rôles", icon: "roles", permission: "users.manage" },
      { href: "/dashboard/personnel", label: "Personnel", icon: "staff", permission: "personnel.view" },
      { href: "/dashboard/parametres", label: "Paramètres", icon: "settings", permission: "settings.view" },
    ],
  },
  {
    title: "Finance",
    items: [
      { href: "/dashboard/finance", label: "Finance", icon: "finance", permission: "payments.view" },
      { href: "/dashboard/paie", label: "Paie", icon: "payroll", permission: "payroll.view" },
      { href: "/dashboard/comptabilite", label: "Comptabilité", icon: "ledger", permission: "reports.view" },
    ],
  },
  {
    title: "Suivi",
    items: [
      { href: "/dashboard/rapports", label: "Rapports", icon: "analytics", permission: "reports.view" },
      { href: "/dashboard/annonces", label: "Annonces", icon: "announcements", permission: "communication.view" },
      { href: "/dashboard/portail", label: "Portail parent", icon: "portal", permission: "parent.portal" },
      { href: "/dashboard/securite", label: "Sécurité", icon: "security", permission: "security.audit" },
    ],
  },
];

const ROUTE_TITLES: Record<string, string> = {
  "/dashboard": "Tableau de bord",
  "/dashboard/utilisateurs": "Utilisateurs",
  "/dashboard/roles": "Rôles",
  "/dashboard/eleves": "Élèves",
  "/dashboard/classes": "Classes",
  "/dashboard/personnel": "Personnel",
  "/dashboard/emploi-du-temps": "Emploi du temps",
  "/dashboard/notes": "Notes",
  "/dashboard/bulletins": "Bulletins",
  "/dashboard/presences": "Présences",
  "/dashboard/finance": "Finance",
  "/dashboard/paie": "Paie",
  "/dashboard/comptabilite": "Comptabilité",
  "/dashboard/rapports": "Rapports",
  "/dashboard/securite": "Sécurité",
  "/dashboard/annonces": "Annonces",
  "/dashboard/portail": "Portail parent",
  "/dashboard/parametres": "Paramètres",
};

export function getPageTitle(pathname: string): string {
  if (ROUTE_TITLES[pathname]) return ROUTE_TITLES[pathname];
  for (const [route, title] of Object.entries(ROUTE_TITLES)) {
    if (route !== "/dashboard" && pathname.startsWith(`${route}/`)) return title;
  }
  return "Tableau de bord";
}
