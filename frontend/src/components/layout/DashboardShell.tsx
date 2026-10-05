"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { AnneeScolaireProvider } from "@/components/layout/AnneeScolaireProvider";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import type { UserInfo } from "@/types/auth";

export function DashboardShell({ user, children }: { user: UserInfo; children: ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const pathname = usePathname();

  const closeNav = useCallback(() => setMobileNavOpen(false), []);

  useEffect(() => {
    closeNav();
  }, [pathname, closeNav]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [mobileNavOpen]);

  return (
    <div className="flex min-h-full flex-1 flex-col bg-slate-50 lg:flex-row">
      {mobileNavOpen && (
        <button
          type="button"
          aria-label="Fermer le menu"
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-[2px] lg:hidden"
          onClick={closeNav}
        />
      )}

      <Sidebar mobileOpen={mobileNavOpen} onNavigate={closeNav} />

      <div className="flex min-w-0 flex-1 flex-col lg:pl-0">
        <AnneeScolaireProvider>
          <Header user={user} onMenuClick={() => setMobileNavOpen(true)} />
          <main className="dashboard-main flex-1 overflow-x-hidden px-3 py-4 sm:px-4 sm:py-5 lg:px-6 lg:py-6">
            {children}
          </main>
        </AnneeScolaireProvider>
      </div>
    </div>
  );
}
