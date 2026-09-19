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
    ? "sgep-status-dot--offline"
    : status === "syncing"
      ? "sgep-status-dot--syncing"
      : pending > 0
        ? "sgep-status-dot--pending"
        : status === "error"
          ? "sgep-status-dot--error"
          : "sgep-status-dot--online";

  return (
    <button
      type="button"
      onClick={() => void syncNow()}
      disabled={!online || status === "syncing"}
      className="sgep-btn-ghost flex items-center gap-2 !px-3 !py-1.5 text-[13px]"
      title={lastMessage ?? "Forcer la synchronisation"}
    >
      <span className={`sgep-status-dot ${dotClass}`} />
      {label}
    </button>
  );
}
