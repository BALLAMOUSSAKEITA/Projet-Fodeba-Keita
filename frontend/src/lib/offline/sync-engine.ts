import { pullSync, pushSync } from "@/lib/api/sync";
import type { SyncQueueItem } from "@/types/sync";
import { getMeta, saveOfflineBundle, setMeta } from "./db";
import { dequeueItem, getPendingItems } from "./sync-queue";

const BUNDLE_KEY = "offline_bundle";
const LAST_SYNC_KEY = "last_sync_at";

export async function pullOfflineData(token: string): Promise<void> {
  const lastSync = await getMeta<string>(LAST_SYNC_KEY);
  const since = lastSync ? `?since=${encodeURIComponent(lastSync)}` : "";
  const data = await pullSync(token, since);
  await saveOfflineBundle(BUNDLE_KEY, data);
  await setMeta(LAST_SYNC_KEY, data.server_time);
}

export async function flushSyncQueue(token: string): Promise<{ applied: number; conflicts: number; errors: number }> {
  const pending = await getPendingItems();
  if (pending.length === 0) {
    return { applied: 0, conflicts: 0, errors: 0 };
  }

  const operations = pending.map((item: SyncQueueItem) => ({
    client_id: item.id,
    entity_type: item.entity_type,
    client_updated_at: item.client_updated_at,
    resolve_strategy: "client_wins" as const,
    payload: item.payload,
  }));

  const response = await pushSync(token, operations);

  for (const result of response.results) {
    if (result.status === "applied" || result.status === "duplicate") {
      await dequeueItem(result.client_id);
    }
  }

  await pullOfflineData(token);
  return {
    applied: response.applied,
    conflicts: response.conflicts,
    errors: response.errors,
  };
}

export async function runFullSync(token: string): Promise<void> {
  await flushSyncQueue(token);
  await pullOfflineData(token);
}

export function isBrowserOnline(): boolean {
  if (typeof navigator === "undefined") return true;
  return navigator.onLine;
}
