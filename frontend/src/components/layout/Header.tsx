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
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-cloud bg-snow px-6">
      <div>
        <h1 className="text-[20px] font-semibold text-obsidian">{getPageTitle(pathname)}</h1>
        <p className="text-[13px] text-steel">Année scolaire 2026-2027</p>
      </div>

      <div className="flex items-center gap-3">
        <SyncStatusIndicator />
        <div className="hidden items-center gap-3 sm:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cloud bg-paper text-[12px] font-semibold text-graphite">
            {initials(user)}
          </div>
          <div className="text-right">
            <p className="text-[14px] font-medium text-graphite">
              {user.prenom} {user.nom}
            </p>
            <p className="text-[12px] text-fog">
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
          className="aw-btn-neutral !py-2 text-[13px]"
        >
          Déconnexion
        </button>
      </div>
    </header>
  );
}
