import type { SyncEntityType, SyncQueueItem } from "@/types/sync";
import { addSyncQueueItem, listSyncQueue, removeSyncQueueItem } from "./db";

function newClientId(): string {
  return `cli-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export async function enqueueSyncOperation(
  entityType: SyncEntityType,
  payload: Record<string, unknown>,
): Promise<SyncQueueItem> {
  const item: SyncQueueItem = {
    id: newClientId(),
    entity_type: entityType,
    client_updated_at: new Date().toISOString(),
    payload,
    created_at: new Date().toISOString(),
  };
  await addSyncQueueItem(item);
  window.dispatchEvent(new CustomEvent("sgep-sync-queue-changed"));
  return item;
}

export async function getPendingCount(): Promise<number> {
  const items = await listSyncQueue<SyncQueueItem>();
  return items.length;
}

export async function getPendingItems(): Promise<SyncQueueItem[]> {
  return listSyncQueue<SyncQueueItem>();
}

export async function dequeueItem(id: string): Promise<void> {
  await removeSyncQueueItem(id);
  window.dispatchEvent(new CustomEvent("sgep-sync-queue-changed"));
}

export function parseOfflineMutation(
  path: string,
  method: string,
  body: string | undefined,
): { entityType: SyncEntityType; payload: Record<string, unknown> } | null {
  if (!body || (method !== "POST" && method !== "PUT" && method !== "PATCH")) {
    return null;
  }

  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(body) as Record<string, unknown>;
  } catch {
    return null;
  }

  if (path === "/api/v1/paiements" && method === "POST") {
    return { entityType: "paiement", payload: parsed };
  }

  return null;
}
