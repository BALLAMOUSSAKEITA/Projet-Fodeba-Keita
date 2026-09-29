"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe } from "@/lib/api/auth";
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
      <div className="flex min-h-full flex-1 items-center justify-center bg-paper">
        <p className="text-[14px] text-fog">Chargement</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-1 bg-paper">
      <SyncProvider />
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header user={user} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
