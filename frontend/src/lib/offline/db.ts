const DB_NAME = "sgep-offline";
const DB_VERSION = 1;

type StoreName = "cache" | "bundle" | "sync_queue" | "meta";

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains("cache")) {
        db.createObjectStore("cache");
      }
      if (!db.objectStoreNames.contains("bundle")) {
        db.createObjectStore("bundle");
      }
      if (!db.objectStoreNames.contains("sync_queue")) {
        db.createObjectStore("sync_queue", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("meta")) {
        db.createObjectStore("meta");
      }
    };
  });
}

async function idbGet<T>(store: StoreName, key: string): Promise<T | null> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readonly");
    const req = tx.objectStore(store).get(key);
    req.onsuccess = () => resolve((req.result as T | undefined) ?? null);
    req.onerror = () => reject(req.error);
  });
}

async function idbPut(store: StoreName, key: string, value: unknown): Promise<void> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readwrite");
    tx.objectStore(store).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function idbDelete(store: StoreName, key: string): Promise<void> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readwrite");
    tx.objectStore(store).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function idbGetAll<T>(store: StoreName): Promise<T[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readonly");
    const req = tx.objectStore(store).getAll();
    req.onsuccess = () => resolve(req.result as T[]);
    req.onerror = () => reject(req.error);
  });
}

export async function cacheGet<T>(key: string): Promise<T | null> {
  if (typeof indexedDB === "undefined") return null;
  return idbGet<T>("cache", key);
}

export async function cacheSet(key: string, value: unknown): Promise<void> {
  if (typeof indexedDB === "undefined") return;
  await idbPut("cache", key, value);
}

export async function saveOfflineBundle(key: string, data: unknown): Promise<void> {
  if (typeof indexedDB === "undefined") return;
  await idbPut("bundle", key, data);
}

export async function getOfflineBundle<T>(key: string): Promise<T | null> {
  if (typeof indexedDB === "undefined") return null;
  return idbGet<T>("bundle", key);
}

export async function getMeta<T>(key: string): Promise<T | null> {
  if (typeof indexedDB === "undefined") return null;
  return idbGet<T>("meta", key);
}

export async function setMeta(key: string, value: unknown): Promise<void> {
  if (typeof indexedDB === "undefined") return;
  await idbPut("meta", key, value);
}

export async function listSyncQueue<T extends { id: string }>(): Promise<T[]> {
  if (typeof indexedDB === "undefined") return [];
  return idbGetAll<T>("sync_queue");
}

export async function addSyncQueueItem<T extends { id: string }>(item: T): Promise<void> {
  if (typeof indexedDB === "undefined") return;
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("sync_queue", "readwrite");
    tx.objectStore("sync_queue").put(item);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

export async function removeSyncQueueItem(id: string): Promise<void> {
  if (typeof indexedDB === "undefined") return;
  await idbDelete("sync_queue", id);
}
