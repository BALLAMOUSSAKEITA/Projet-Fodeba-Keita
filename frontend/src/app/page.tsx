"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getUser } from "@/lib/auth/session";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const user = getUser();
    router.replace(user ? "/dashboard" : "/login");
  }, [router]);

  return (
    <div className="flex min-h-full flex-1 items-center justify-center bg-slate-50">
      <p className="text-sm text-slate-500">Redirection...</p>
    </div>
  );
}
