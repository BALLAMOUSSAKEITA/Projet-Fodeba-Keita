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
    <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-[14px] text-amber-700">
      ⚠️ Votre session a expiré. Connectez-vous à nouveau.
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
      {/* Left panel — branding */}
      <div className="relative hidden w-[480px] flex-col justify-between overflow-hidden bg-slate-900 p-10 lg:flex">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-600/20 via-transparent to-amber-500/10" />
        <div className="relative z-10">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-600 shadow-lg">
            <svg viewBox="0 0 24 24" className="h-6 w-6" aria-hidden>
              <path d="M12 3 4 7v10l8 4 8-4V7l-8-4Z" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinejoin="round" />
              <path d="M12 7v10" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <h1 className="mt-8 text-[36px] font-bold leading-tight text-white">
            Groupe Scolaire<br />Privé Fodeba Keita
          </h1>
          <p className="mt-4 max-w-sm text-[16px] leading-relaxed text-slate-300">
            Inscriptions, notes, finance et communication avec les familles —
            une plateforme moderne pour votre établissement.
          </p>
          <div className="mt-8 flex flex-wrap gap-2">
            <span className="rounded-lg bg-white/10 px-3 py-1.5 text-[12px] font-medium text-white backdrop-blur-sm">
              Maternelle
            </span>
            <span className="rounded-lg bg-white/10 px-3 py-1.5 text-[12px] font-medium text-white backdrop-blur-sm">
              Primaire
            </span>
            <span className="rounded-lg bg-teal-500/20 px-3 py-1.5 text-[12px] font-medium text-teal-300 backdrop-blur-sm">
              Rentrée 2026-2027
            </span>
          </div>
        </div>
        <p className="relative z-10 text-[13px] text-slate-500">📍 Conakry, Guinée</p>
      </div>

      {/* Right panel — login form */}
      <div className="flex flex-1 items-center justify-center bg-slate-50 px-6 py-12">
        <div className="w-full max-w-md">
          <LogoLight className="mb-8 lg:hidden" />

          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
            <h2 className="text-[28px] font-bold text-slate-900">Connexion</h2>
            <p className="mt-2 text-[14px] text-slate-500">Identifiants fournis par l&apos;administration</p>

            <Suspense fallback={null}>
              <SessionExpiredNotice />
            </Suspense>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="mb-1.5 block text-[14px] font-medium text-slate-700">
                  Adresse e-mail
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-[14px] text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
                  placeholder="nom@fodebakeita.gn"
                />
              </div>
              <div>
                <label htmlFor="password" className="mb-1.5 block text-[14px] font-medium text-slate-700">
                  Mot de passe
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-[14px] text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
                />
              </div>

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-[14px] text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-teal-600 px-4 py-2.5 text-[14px] font-semibold text-white shadow-sm transition hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Connexion en cours…" : "Se connecter"}
              </button>
            </form>

            <p className="mt-5 text-center">
              <a href="/forgot-password" className="text-[14px] font-medium text-teal-600 hover:underline">
                Mot de passe oublié ?
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
