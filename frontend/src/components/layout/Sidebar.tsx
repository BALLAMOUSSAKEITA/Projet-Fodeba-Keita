"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/session";
import { NAV_SECTIONS, filterVisibleNavItems } from "@/lib/navigation";
import { NavIcon } from "@/components/ui/NavIcon";
import { Logo } from "@/components/layout/Logo";

function isActive(pathname: string, href: string): boolean {
  return pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`));
}

type SidebarProps = {
  mobileOpen?: boolean;
  onNavigate?: () => void;
};

export function Sidebar({ mobileOpen = false, onNavigate }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={`fd-sidebar fixed inset-y-0 left-0 z-50 flex w-[min(288px,88vw)] flex-col shadow-xl transition-transform duration-200 ease-out lg:static lg:z-auto lg:w-[260px] lg:shrink-0 lg:translate-x-0 lg:shadow-none ${
        mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      }`}
      aria-hidden={!mobileOpen ? undefined : false}
    >
      <div className="flex items-center justify-between gap-2 px-4 py-4 sm:px-5 sm:py-5">
        <Logo />
        <button
          type="button"
          className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          aria-label="Fermer le menu"
          onClick={onNavigate}
        >
          <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto overscroll-contain px-3 pb-4">
        {NAV_SECTIONS.map((section) => {
          const items = filterVisibleNavItems(section.items, (p) => !p || hasPermission(p));
          if (items.length === 0) return null;

          return (
            <div key={section.title} className="mb-5 last:mb-0">
              <p className="mb-1.5 px-3 text-[11px] font-medium uppercase tracking-wider text-slate-500">
                {section.title}
              </p>
              <ul className="space-y-0.5">
                {items.map((item) => {
                  const active = isActive(pathname, item.href);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={onNavigate}
                        className={`aw-nav-link min-h-[44px] ${active ? "aw-nav-link-active" : ""}`}
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

      <div className="border-t border-white/10 px-5 py-4">
        <p className="text-xs font-medium text-slate-400">Commune de Matam</p>
        <p className="text-[11px] text-slate-500">Tél. 626 137 290</p>
      </div>
    </aside>
  );
}
