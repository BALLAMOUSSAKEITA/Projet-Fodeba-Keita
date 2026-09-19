"use client";

import { useRouter } from "next/navigation";
import type { UserInfo } from "@/types/auth";
import { ROLE_LABELS, clearSession } from "@/lib/auth/session";
import { SyncStatusIndicator } from "@/components/layout/SyncStatusIndicator";

interface HeaderProps {
  user: UserInfo;
}

export function Header({ user }: HeaderProps) {
  const router = useRouter();

  function handleLogout() {
    clearSession();
    router.push("/login");
  }

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">Tableau de bord</h1>
        <p className="text-sm text-slate-500">Année scolaire 2025–2026</p>
      </div>

      <div className="flex items-center gap-4">
        <SyncStatusIndicator />
        <div className="text-right">
          <p className="text-sm font-medium text-slate-900">
            {user.prenom} {user.nom}
          </p>
          <p className="text-xs text-slate-500">
            {ROLE_LABELS[user.role] ?? user.role.replace("_", " ")}
          </p>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700 transition hover:bg-slate-50"
        >
          Déconnexion
        </button>
      </div>
    </header>
  );
}
