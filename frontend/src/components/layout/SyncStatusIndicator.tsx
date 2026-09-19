"use client";

import { useCallback, useEffect, useState } from "react";
import { getToken } from "@/lib/auth/session";
import { getPendingCount } from "@/lib/offline/sync-queue";
import { isBrowserOnline, runFullSync } from "@/lib/offline/sync-engine";
import type { SyncStatus } from "@/types/sync";

export function SyncStatusIndicator() {
  const [online, setOnline] = useState(true);
  const [pending, setPending] = useState(0);
  const [status, setStatus] = useState<SyncStatus>("idle");
  const [lastMessage, setLastMessage] = useState<string | null>(null);

  const refreshPending = useCallback(async () => {
    setPending(await getPendingCount());
  }, []);

  const syncNow = useCallback(async () => {
    const token = getToken();
    if (!token || !isBrowserOnline()) return;
    setStatus("syncing");
    setLastMessage(null);
    try {
      await runFullSync(token);
      await refreshPending();
      setStatus("idle");
      setLastMessage("Synchronisation terminée");
    } catch {
      setStatus("error");
      setLastMessage("Échec de synchronisation");
    }
  }, [refreshPending]);

  useEffect(() => {
    setOnline(isBrowserOnline());
    refreshPending();

    const onOnline = () => {
      setOnline(true);
      void syncNow();
    };
    const onOffline = () => {
      setOnline(false);
      setStatus("offline");
    };
    const onQueueChange = () => {
      void refreshPending();
    };

    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    window.addEventListener("sgep-sync-queue-changed", onQueueChange);

    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
      window.removeEventListener("sgep-sync-queue-changed", onQueueChange);
    };
  }, [refreshPending, syncNow]);

  const label = !online
    ? "Hors ligne"
    : status === "syncing"
      ? "Synchronisation…"
      : pending > 0
        ? `${pending} en attente`
        : "En ligne";

  const dotClass = !online
    ? "bg-amber-500"
    : status === "syncing"
      ? "bg-blue-500 animate-pulse"
      : pending > 0
        ? "bg-orange-500"
        : status === "error"
          ? "bg-red-500"
          : "bg-emerald-500";

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => void syncNow()}
        disabled={!online || status === "syncing"}
        className="flex items-center gap-2 rounded-lg border border-slate-200 px-2.5 py-1 text-xs text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        title={lastMessage ?? "Forcer la synchronisation"}
      >
        <span className={`h-2 w-2 rounded-full ${dotClass}`} />
        {label}
      </button>
    </div>
  );
}
