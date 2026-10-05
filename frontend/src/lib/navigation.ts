export type NavIconName =
  | "dashboard"
  | "users"
  | "students"
  | "classes"
  | "staff"
  | "calendar"
  | "finance"
  | "payroll"
  | "ledger"
  | "analytics";

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
      { href: "/dashboard/classes", label: "Classes", icon: "classes", permission: "students.view" },
      { href: "/dashboard/eleves", label: "Élèves", icon: "students", permission: "students.view" },
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
      { href: "/dashboard/personnel", label: "Personnel", icon: "staff", permission: "personnel.view" },
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
    ],
  },
];

const ROUTE_TITLES: Record<string, string> = {
  "/dashboard": "Tableau de bord",
  "/dashboard/utilisateurs": "Utilisateurs",
  "/dashboard/eleves": "Élèves",
  "/dashboard/classes": "Classes",
  "/dashboard/personnel": "Personnel",
  "/dashboard/emploi-du-temps": "Emploi du temps",
  "/dashboard/finance": "Finance",
  "/dashboard/paie": "Paie",
  "/dashboard/comptabilite": "Comptabilité",
  "/dashboard/rapports": "Rapports",
};

export function filterVisibleNavItems(
  items: NavItem[],
  hasAccess: (permission?: string) => boolean,
): NavItem[] {
  return items.filter((item) => !item.permission || hasAccess(item.permission));
}

export function getPageTitle(pathname: string): string {
  if (ROUTE_TITLES[pathname]) return ROUTE_TITLES[pathname];
  for (const [route, title] of Object.entries(ROUTE_TITLES)) {
    if (route !== "/dashboard" && pathname.startsWith(`${route}/`)) return title;
  }
  return "Tableau de bord";
}
