"use client";



import Link from "next/link";

import { usePathname } from "next/navigation";

import { hasPermission } from "@/lib/auth/session";



type NavItem = {

  href: string;

  label: string;

  abbr: string;

  permission?: string;

  disabled?: boolean;

};



const NAV_ITEMS: NavItem[] = [

  { href: "/dashboard", label: "Tableau de bord", abbr: "TD" },

  { href: "/dashboard/utilisateurs", label: "Utilisateurs", abbr: "U", permission: "users.manage" },

  { href: "/dashboard/roles", label: "Rôles", abbr: "R", permission: "users.manage" },

  { href: "/dashboard/eleves", label: "Élèves", abbr: "É", permission: "students.view" },

  { href: "/dashboard/classes", label: "Classes", abbr: "C", permission: "students.view" },

  { href: "/dashboard/personnel", label: "Personnel", abbr: "P", permission: "personnel.view" },

  { href: "/dashboard/emploi-du-temps", label: "Emploi du temps", abbr: "ED", permission: "timetable.view" },

  { href: "/dashboard/notes", label: "Notes", abbr: "N", permission: "grades.modify" },

  { href: "/dashboard/bulletins", label: "Bulletins", abbr: "B", permission: "grades.validate_bulletins" },

  { href: "/dashboard/presences", label: "Présences", abbr: "Pr", permission: "attendance.view" },

  { href: "/dashboard/finance", label: "Finance", abbr: "F", permission: "payments.view" },

  { href: "/dashboard/paie", label: "Paie", abbr: "Pa", permission: "payroll.view" },

  { href: "/dashboard/comptabilite", label: "Comptabilité", abbr: "Co", permission: "reports.view" },

  { href: "/dashboard/rapports", label: "Rapports", abbr: "Rp", permission: "reports.view" },

  { href: "/dashboard/securite", label: "Sécurité", abbr: "S", permission: "security.audit" },

  { href: "/dashboard/annonces", label: "Annonces", abbr: "A", permission: "communication.view" },

  { href: "/dashboard/portail", label: "Portail parent", abbr: "PP", permission: "parent.portal" },

  { href: "/dashboard/parametres", label: "Paramètres", abbr: "Pm", permission: "settings.view" },

];



export function Sidebar() {

  const pathname = usePathname();



  return (

    <aside className="flex w-64 flex-col border-r border-hairline bg-marble">

      <div className="border-b border-hairline px-6 py-5">

        <p className="text-[13px] font-semibold uppercase tracking-wider text-graphite-ink">

          SGEP

        </p>

        <h2 className="mt-1 text-sm font-semibold leading-snug text-graphite-ink">

          Groupe Scolaire Privé

          <br />

          Fodeba Keita

        </h2>

      </div>



      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">

        {NAV_ITEMS.map((item) => {

          if (item.permission && !hasPermission(item.permission)) {

            return null;

          }



          const isActive =

            pathname === item.href ||

            (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));

          const className = [

            "flex items-center gap-3 rounded-[6px] px-3 py-2 text-[14px] font-medium transition-colors",

            item.disabled

              ? "cursor-not-allowed text-ash"

              : isActive

                ? "bg-drafting-gray text-graphite-ink"

                : "text-steel hover:bg-drafting-gray/60 hover:text-graphite-ink",

          ].join(" ");



          const badge = (

            <span

              className={[

                "sgep-nav-badge",

                isActive && !item.disabled ? "bg-hairline text-graphite-ink" : "",

              ]

                .filter(Boolean)

                .join(" ")}

            >

              {item.abbr}

            </span>

          );



          if (item.disabled) {

            return (

              <span key={item.href} className={className} title="Bientôt disponible">

                {badge}

                {item.label}

              </span>

            );

          }



          return (

            <Link key={item.href} href={item.href} className={className}>

              {badge}

              {item.label}

            </Link>

          );

        })}

      </nav>



      <div className="border-t border-hairline p-4 text-[13px] text-ash">

        Conakry, Guinée

      </div>

    </aside>

  );

}

