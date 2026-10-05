"use client";

import { FormEvent, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { login } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import { ApiError } from "@/lib/api/client";
import { LogoLight } from "@/components/layout/Logo";

function SessionExpiredNotice() {
  const searchParams = useSearchParams();
  if (searchParams.get("session") !== "expired") return null;
  return (
    <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      Votre session a expiré. Connectez-vous à nouveau.
    </div>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await login({ email, password });
      saveSession(response.access_token, response.refresh_token, response.user);
      router.push("/dashboard");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Connexion impossible. Vérifiez le réseau et le serveur.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-1">
      <div className="hidden w-[420px] flex-col justify-between bg-slate-900 p-10 lg:flex">
        <div>
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-teal-600">
            <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
              <path
                d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
                fill="none"
                stroke="#fff"
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
              <path d="M12 7v10" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <h1 className="mt-8 text-3xl font-bold leading-tight text-white">
            Groupe scolaire privé
            <br />
            Fodeba Keita
          </h1>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-slate-400">
            Gestion des inscriptions, classes, finances et personnel.
          </p>
        </div>
        <p className="text-xs text-slate-500">Conakry, Guinée</p>
      </div>

      <div className="flex flex-1 items-center justify-center bg-slate-50 px-6 py-12">
        <div className="w-full max-w-md">
          <LogoLight className="mb-8 lg:hidden" />

          <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900">Connexion</h2>
            <p className="mt-2 text-sm text-slate-500">Identifiants fournis par l&apos;administration</p>

            <Suspense fallback={null}>
              <SessionExpiredNotice />
            </Suspense>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Adresse e-mail
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
                  placeholder="nom@fodebakeita.gn"
                />
              </div>
              <div>
                <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Mot de passe
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
                />
              </div>

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Connexion en cours…" : "Se connecter"}
              </button>
            </form>

            <p className="mt-5 text-center">
              <a href="/forgot-password" className="text-sm font-medium text-teal-600 hover:underline">
                Mot de passe oublié
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
