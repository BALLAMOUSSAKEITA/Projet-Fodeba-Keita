"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/session";
import { NAV_SECTIONS } from "@/lib/navigation";
import { NavIcon } from "@/components/ui/NavIcon";
import { Logo } from "@/components/layout/Logo";

function isNavActive(pathname: string, href: string): boolean {
  return pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`));
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-[260px] shrink-0 flex-col border-r border-hairline bg-marble">
      <div className="border-b border-hairline px-5 py-5">
        <Logo />
        <p className="mt-3 text-[12px] leading-relaxed text-steel">
          Groupe Scolaire Privé
          <br />
          Conakry, Guinée
        </p>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {NAV_SECTIONS.map((section) => {
          const visibleItems = section.items.filter(
            (item) => !item.permission || hasPermission(item.permission),
          );
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.title} className="mb-5 last:mb-0">
              <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-[0.08em] text-ash">
                {section.title}
              </p>
              <ul className="space-y-0.5">
                {visibleItems.map((item) => {
                  const active = isNavActive(pathname, item.href);
                  const className = [
                    "sgep-nav-link",
                    active ? "sgep-nav-link-active" : "",
                    item.disabled ? "sgep-nav-link-disabled" : "",
                  ]
                    .filter(Boolean)
                    .join(" ");

                  const content = (
                    <>
                      <NavIcon name={item.icon} className="shrink-0 opacity-80" />
                      <span className="truncate">{item.label}</span>
                    </>
                  );

                  return (
                    <li key={item.href}>
                      {item.disabled ? (
                        <span className={className} title="Bientôt disponible">
                          {content}
                        </span>
                      ) : (
                        <Link href={item.href} className={className}>
                          {content}
                        </Link>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
