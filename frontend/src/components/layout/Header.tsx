"use client";

import { usePathname, useRouter } from "next/navigation";
import type { UserInfo } from "@/types/auth";
import { ROLE_LABELS, clearSession } from "@/lib/auth/session";
import { getPageTitle } from "@/lib/navigation";
import { useAnneeScolaire } from "@/components/layout/AnneeScolaireProvider";
import { SyncStatusIndicator } from "@/components/layout/SyncStatusIndicator";

interface HeaderProps {
  user: UserInfo;
  onMenuClick?: () => void;
}

function initials(user: UserInfo): string {
  const a = user.prenom?.charAt(0) ?? "";
  const b = user.nom?.charAt(0) ?? "";
  return (a + b).toUpperCase() || "U";
}

export function Header({ user, onMenuClick }: HeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { annees, anneeId, setAnneeId, loading: anneesLoading } = useAnneeScolaire();
  const title = getPageTitle(pathname);

  return (
    <header className="sticky top-0 z-30 flex min-h-14 flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-white px-3 py-2 shadow-sm sm:min-h-16 sm:gap-3 sm:px-4 lg:px-6">
      <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 lg:hidden"
          aria-label="Ouvrir le menu"
        >
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
          </svg>
        </button>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-base font-semibold text-slate-900 sm:text-lg">{title}</h1>
          {!anneesLoading && annees.length > 0 && (
            <label className="mt-0.5 block sm:mt-1 sm:hidden">
              <span className="sr-only">Année scolaire</span>
              <select
                value={anneeId}
                onChange={(e) => setAnneeId(e.target.value)}
                className="max-w-full rounded-md border border-slate-200 bg-white py-1 pl-2 pr-7 text-xs text-slate-700"
              >
                {annees.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.libelle}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        {!anneesLoading && annees.length > 0 && (
          <label className="hidden shrink-0 text-sm sm:block">
            <span className="sr-only">Année scolaire</span>
            <select
              value={anneeId}
              onChange={(e) => setAnneeId(e.target.value)}
              className="max-w-[9rem] rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-sm text-slate-700 md:max-w-none"
            >
              {annees.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.libelle}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:gap-3">
        <SyncStatusIndicator />
        <div className="hidden items-center gap-2 md:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-600 text-xs font-semibold text-white">
            {initials(user)}
          </div>
          <div className="max-w-[140px] text-right lg:max-w-none">
            <p className="truncate text-sm font-medium text-slate-800">
              {user.prenom} {user.nom}
            </p>
            <p className="truncate text-xs text-slate-400">
              {ROLE_LABELS[user.role] ?? user.role.replace("_", " ")}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => {
            clearSession();
            router.push("/login");
          }}
          className="rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-medium text-slate-600 hover:border-red-200 hover:bg-red-50 hover:text-red-600 sm:px-3 sm:text-[13px]"
        >
          Quitter
        </button>
      </div>
    </header>
  );
}
