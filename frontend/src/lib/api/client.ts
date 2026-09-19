import { cacheGet, cacheSet } from "@/lib/offline/db";
import { enqueueSyncOperation, parseOfflineMutation } from "@/lib/offline/sync-queue";
import { isBrowserOnline } from "@/lib/offline/sync-engine";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class OfflineQueuedError extends Error {
  constructor(public clientId: string) {
    super("Opération mise en file d'attente (hors ligne)");
    this.name = "OfflineQueuedError";
  }
}

function cacheKey(path: string, token?: string | null): string {
  return token ? `${path}::${token.slice(-8)}` : path;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const offlineMutation = parseOfflineMutation(path, method, options.body as string | undefined);

  if (!isBrowserOnline()) {
    if (method === "GET") {
      const cached = await cacheGet<T>(cacheKey(path, token));
      if (cached !== null) return cached;
      throw new ApiError("Données indisponibles hors ligne", 503);
    }
    if (offlineMutation) {
      const item = await enqueueSyncOperation(offlineMutation.entityType, offlineMutation.payload);
      throw new OfflineQueuedError(item.id);
    }
    throw new ApiError("Connexion requise pour cette action", 503);
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    if (method === "GET") {
      const cached = await cacheGet<T>(cacheKey(path, token));
      if (cached !== null) return cached;
    }
    if (offlineMutation) {
      const item = await enqueueSyncOperation(offlineMutation.entityType, offlineMutation.payload);
      throw new OfflineQueuedError(item.id);
    }
    throw new ApiError("Réseau indisponible", 503);
  }

  if (!response.ok) {
    let detail = "Une erreur est survenue";
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(
      typeof detail === "string" ? detail : "Une erreur est survenue",
      response.status,
    );
  }

  const data = (await response.json()) as T;

  if (method === "GET") {
    await cacheSet(cacheKey(path, token), data);
  }

  return data;
}

export async function apiDownload(
  path: string,
  token: string,
  filename: string,
): Promise<void> {
  if (!isBrowserOnline()) {
    throw new ApiError("Téléchargement indisponible hors ligne", 503);
  }

  const response = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    let detail = "Erreur lors du téléchargement";
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(
      typeof detail === "string" ? detail : "Erreur lors du téléchargement",
      response.status,
    );
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
