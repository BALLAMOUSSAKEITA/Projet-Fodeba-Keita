"use client";

import { useEffect } from "react";
import { getToken } from "@/lib/auth/session";
import { isBrowserOnline, pullOfflineData } from "@/lib/offline/sync-engine";

export function SyncProvider() {
  useEffect(() => {
    const token = getToken();
    if (!token || !isBrowserOnline()) return;
    pullOfflineData(token).catch(() => {
      // Pull initial silencieux
    });
  }, []);

  return null;
}
