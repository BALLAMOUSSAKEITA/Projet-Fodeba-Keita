"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe } from "@/lib/api/auth";
import { AnneeScolaireProvider } from "@/components/layout/AnneeScolaireProvider";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { SyncProvider } from "@/components/offline/SyncProvider";
import { getRefreshToken, getToken, getUser, saveSession } from "@/lib/auth/session";
import type { UserInfo } from "@/types/auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const sessionUser = getUser();
    const token = getToken();
    if (!sessionUser || !token) {
      router.replace("/login");
      return;
    }

    getMe(token)
      .then((freshUser) => {
        const access = getToken();
        const refresh = getRefreshToken();
        if (access && refresh) {
          saveSession(access, refresh, freshUser);
        }
        setUser(freshUser);
        setChecking(false);
      })
      .catch(() => {
        setChecking(false);
        router.replace("/login?session=expired");
      });
  }, [router]);

  if (checking || !user) {
    return (
      <div className="flex min-h-full flex-1 items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal-200 border-t-teal-600" />
          <p className="text-[14px] text-slate-400">Chargement…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-1 bg-slate-50">
      <SyncProvider />
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <AnneeScolaireProvider>
          <Header user={user} />
          <main className="flex-1 p-6">{children}</main>
        </AnneeScolaireProvider>
      </div>
    </div>
  );
}
