"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/session";
import { NAV_SECTIONS } from "@/lib/navigation";
import { NavIcon } from "@/components/ui/NavIcon";
import { Logo } from "@/components/layout/Logo";

function isActive(pathname: string, href: string): boolean {
  return pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`));
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-[260px] shrink-0 flex-col border-r border-cloud bg-snow">
      <div className="px-5 py-5">
        <Logo />
        <span className="aw-badge-ember mt-4">2025-2026</span>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        {NAV_SECTIONS.map((section) => {
          const items = section.items.filter((i) => !i.permission || hasPermission(i.permission));
          if (items.length === 0) return null;

          return (
            <div key={section.title} className="mb-5 last:mb-0">
              <p className="mb-1.5 px-3 text-[11px] font-medium uppercase tracking-wide text-fog">
                {section.title}
              </p>
              <ul className="space-y-0.5">
                {items.map((item) => {
                  const active = isActive(pathname, item.href);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={`aw-nav-link ${active ? "aw-nav-link-active" : ""}`}
                      >
                        <NavIcon name={item.icon} />
                        {item.label}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </nav>

      <div className="border-t border-cloud px-5 py-4">
        <p className="text-[12px] text-fog">Conakry, Guinée</p>
      </div>
    </aside>
  );
}
