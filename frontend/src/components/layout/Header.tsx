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
    <header className="flex h-16 items-center justify-between border-b border-silver-mist/20 bg-midnight-navy px-6">
      <div>
        <h1 className="font-display text-[28px] font-light leading-none tracking-[-0.56px] text-canvas-white">
          {getPageTitle(pathname)}
        </h1>
        <p className="mt-1 font-mono text-[11px] uppercase tracking-[0.06em] text-silver-mist">
          Année scolaire 2025-2026
        </p>
      </div>

      <div className="flex items-center gap-3">
        <SyncStatusIndicator />
        <div className="hidden items-center gap-3 sm:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full border border-silver-mist/35 text-[12px] font-semibold text-canvas-white">
            {initials(user)}
          </div>
          <div className="text-right">
            <p className="text-[14px] font-medium text-canvas-white">
              {user.prenom} {user.nom}
            </p>
            <p className="text-[12px] text-silver-mist">
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
          className="ws-btn-ghost !px-4 !py-2 text-[13px]"
        >
          Déconnexion
        </button>
      </div>
    </header>
  );
}
