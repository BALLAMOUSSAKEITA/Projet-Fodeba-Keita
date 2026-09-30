"use client";

import { usePathname, useRouter } from "next/navigation";
import type { UserInfo } from "@/types/auth";
import { ROLE_LABELS, clearSession } from "@/lib/auth/session";
import { getPageTitle } from "@/lib/navigation";
import { SyncStatusIndicator } from "@/components/layout/SyncStatusIndicator";

interface HeaderProps {
  user: UserInfo;
}

function initials(user: UserInfo): string {
  const a = user.prenom?.charAt(0) ?? "";
  const b = user.nom?.charAt(0) ?? "";
  return (a + b).toUpperCase() || "U";
}

export function Header({ user }: HeaderProps) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm">
      <div>
        <h1 className="text-[18px] font-semibold text-slate-900">{getPageTitle(pathname)}</h1>
        <p className="text-[12px] text-slate-400">Année scolaire 2026-2027</p>
      </div>

      <div className="flex items-center gap-3">
        <SyncStatusIndicator />
        <div className="hidden items-center gap-3 sm:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-teal-600 text-[12px] font-bold text-white shadow-sm">
            {initials(user)}
          </div>
          <div className="text-right">
            <p className="text-[14px] font-medium text-slate-800">
              {user.prenom} {user.nom}
            </p>
            <p className="text-[12px] text-slate-400">
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
          className="rounded-lg border border-slate-200 px-3 py-2 text-[13px] font-medium text-slate-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
        >
          Déconnexion
        </button>
      </div>
    </header>
  );
}
