"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { SyncProvider } from "@/components/offline/SyncProvider";
import { getUser } from "@/lib/auth/session";
import type { UserInfo } from "@/types/auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);

  useEffect(() => {
    const sessionUser = getUser();
    if (!sessionUser) {
      router.replace("/login");
      return;
    }
    setUser(sessionUser);
  }, [router]);

  if (!user) {
    return (
      <div className="flex min-h-full flex-1 items-center justify-center bg-midnight-navy">
        <p className="font-mono text-[12px] uppercase tracking-[0.06em] text-silver-mist">
          Chargement
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-1 bg-midnight-navy">
      <SyncProvider />
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header user={user} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
