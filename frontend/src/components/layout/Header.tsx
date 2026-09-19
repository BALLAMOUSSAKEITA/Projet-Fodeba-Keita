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
    <header className="flex h-16 items-center justify-between border-b border-hairline bg-marble px-6">
      <div>
        <h1 className="text-[20px] font-medium leading-tight text-graphite-ink">
          Tableau de bord
        </h1>
        <p className="text-[13px] text-steel">Année scolaire 2025–2026</p>
      </div>

      <div className="flex items-center gap-4">
        <SyncStatusIndicator />
        <div className="hidden text-right sm:block">
          <p className="text-[14px] font-medium text-graphite-ink">
            {user.prenom} {user.nom}
          </p>
          <p className="text-[13px] text-steel">
            {ROLE_LABELS[user.role] ?? user.role.replace("_", " ")}
          </p>
        </div>
        <button type="button" onClick={handleLogout} className="sgep-btn-pill">
          Déconnexion
        </button>
      </div>
    </header>
  );
}
