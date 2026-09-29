import { cacheGet, cacheSet } from "@/lib/offline/db";
import { enqueueSyncOperation, parseOfflineMutation } from "@/lib/offline/sync-queue";
import { isBrowserOnline } from "@/lib/offline/sync-engine";
import {
  clearSession,
  getRefreshToken,
  getToken,
  saveSession,
} from "@/lib/auth/session";
import type { LoginResponse } from "@/types/auth";

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

let refreshInFlight: Promise<boolean> | null = null;

function isAuthPath(path: string): boolean {
  return path.includes("/auth/login") || path.includes("/auth/refresh");
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  clearSession();
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/forgot-password") || path.startsWith("/reset-password")) {
    return;
  }
  window.location.replace("/login?session=expired");
}

async function tryRefreshSession(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!response.ok) return false;
        const data = (await response.json()) as LoginResponse;
        saveSession(data.access_token, data.refresh_token, data.user);
        return true;
      } catch {
        return false;
      } finally {
        refreshInFlight = null;
      }
    })();
  }

  return refreshInFlight;
}

function cacheKey(path: string, token?: string | null): string {
  return token ? `${path}::${token.slice(-8)}` : path;
}

async function parseErrorDetail(response: Response): Promise<string> {
  let detail = "Une erreur est survenue";
  try {
    const body = await response.json();
    detail = body.detail ?? detail;
  } catch {
    // ignore
  }
  return typeof detail === "string" ? detail : "Une erreur est survenue";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
  retriedAfterRefresh = false,
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

  const authToken = token ?? getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };

  if (authToken) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${authToken}`;
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

  if (response.status === 401 && !retriedAfterRefresh && !isAuthPath(path)) {
    const refreshed = await tryRefreshSession();
    if (refreshed) {
      return apiFetch<T>(path, options, getToken(), true);
    }
    redirectToLogin();
    throw new ApiError("Session expirée. Reconnectez-vous.", 401);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response), response.status);
  }

  const data = (await response.json()) as T;

  if (method === "GET") {
    await cacheSet(cacheKey(path, authToken), data);
  }

  return data;
}

export async function apiDownload(
  path: string,
  token: string,
  filename: string,
  retriedAfterRefresh = false,
): Promise<void> {
  if (!isBrowserOnline()) {
    throw new ApiError("Téléchargement indisponible hors ligne", 503);
  }

  const authToken = token || getToken() || "";
  const response = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });

  if (response.status === 401 && !retriedAfterRefresh) {
    const refreshed = await tryRefreshSession();
    if (refreshed) {
      const next = getToken();
      if (next) return apiDownload(path, next, filename, true);
    }
    redirectToLogin();
    throw new ApiError("Session expirée. Reconnectez-vous.", 401);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response), response.status);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
