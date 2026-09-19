"use client";

import { useEffect, useState } from "react";
import { listRoles } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Role } from "@/types/auth";

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    listRoles(token)
      .then(setRoles)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Erreur de chargement"),
      )
      .finally(() => setLoading(false));
  }, []);

  if (!hasPermission("users.manage")) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Réservé aux administrateurs.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Rôles et permissions</h2>
        <p className="text-sm text-slate-500">
          Matrice des droits d&apos;accès du système
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Chargement...</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {roles.map((role) => (
            <div
              key={role.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">{role.label}</h3>
                  <p className="text-xs text-slate-500">{role.code}</p>
                </div>
                {role.is_system && (
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                    Système
                  </span>
                )}
              </div>
              {role.description && (
                <p className="mt-2 text-sm text-slate-600">{role.description}</p>
              )}
              <div className="mt-4 flex flex-wrap gap-1.5">
                {role.permissions.map((perm) => (
                  <span
                    key={perm.id}
                    className="rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-800"
                    title={perm.description}
                  >
                    {perm.code}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
