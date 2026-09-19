"use client";

import { usePathname, useRouter } from "next/navigation";
import type { UserInfo } from "@/types/auth";
import { ROLE_LABELS, clearSession } from "@/lib/auth/session";
import { getPageTitle } from "@/lib/navigation";
import { SyncStatusIndicator } from "@/components/layout/SyncStatusIndicator";

interface HeaderProps {
  user: UserInfo;
}

function userInitials(user: UserInfo): string {
  const first = user.prenom?.trim().charAt(0) ?? "";
  const last = user.nom?.trim().charAt(0) ?? "";
  return (first + last).toUpperCase() || "U";
}

export function Header({ user }: HeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const pageTitle = getPageTitle(pathname);

  function handleLogout() {
    clearSession();
    router.push("/login");
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-hairline bg-marble px-6">
      <div>
        <h1 className="text-[20px] font-medium leading-tight tracking-[-0.01em] text-graphite-ink">
          {pageTitle}
        </h1>
        <p className="text-[13px] text-steel">Année scolaire 2025-2026</p>
      </div>

      <div className="flex items-center gap-3">
        <SyncStatusIndicator />
        <div className="hidden items-center gap-3 sm:flex">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-full border border-hairline bg-drafting-gray text-[13px] font-semibold text-graphite-ink"
            aria-hidden
          >
            {userInitials(user)}
          </div>
          <div className="text-right">
            <p className="text-[14px] font-medium leading-tight text-graphite-ink">
              {user.prenom} {user.nom}
            </p>
            <p className="text-[12px] text-steel">
              {ROLE_LABELS[user.role] ?? user.role.replace("_", " ")}
            </p>
          </div>
        </div>
        <button type="button" onClick={handleLogout} className="sgep-btn-pill">
          Déconnexion
        </button>
      </div>
    </header>
  );
}
