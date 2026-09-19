import type { SyncPullResponse, SyncPushResponse } from "@/types/sync";
import { apiFetch } from "./client";

export async function pullSync(token: string, query = ""): Promise<SyncPullResponse> {
  return apiFetch<SyncPullResponse>(`/api/v1/sync/pull${query}`, {}, token);
}

export async function pushSync(
  token: string,
  operations: {
    client_id: string;
    entity_type: string;
    client_updated_at: string;
    resolve_strategy?: string;
    payload: Record<string, unknown>;
  }[],
): Promise<SyncPushResponse> {
  return apiFetch<SyncPushResponse>(
    "/api/v1/sync/push",
    { method: "POST", body: JSON.stringify({ operations }) },
    token,
  );
}
