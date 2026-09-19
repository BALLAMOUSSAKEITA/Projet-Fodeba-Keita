"use client";



import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import { AnnouncementBar } from "@/components/layout/AnnouncementBar";

import { Header } from "@/components/layout/Header";

import { Sidebar } from "@/components/layout/Sidebar";

import { SyncProvider } from "@/components/offline/SyncProvider";

import { getUser } from "@/lib/auth/session";

import type { UserInfo } from "@/types/auth";



export default function DashboardLayout({

  children,

}: {

  children: React.ReactNode;

}) {

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

      <div className="flex min-h-full flex-1 items-center justify-center bg-drafting-gray">

        <p className="text-[14px] text-steel">Chargement</p>

      </div>

    );

  }



  return (

    <div className="flex min-h-full flex-1 flex-col bg-drafting-gray">

      <AnnouncementBar />

      <div className="flex flex-1">

        <SyncProvider />

        <Sidebar />

        <div className="flex flex-1 flex-col">

          <Header user={user} />

          <main className="flex-1 p-6">{children}</main>

        </div>

      </div>

    </div>

  );

}

