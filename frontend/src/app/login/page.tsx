"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import { ApiError } from "@/lib/api/client";
import { AuroraRibbon } from "@/components/ui/AuroraRibbon";
import { Logo } from "@/components/layout/Logo";

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
    <div className="relative flex min-h-full flex-1 overflow-hidden bg-midnight-navy">
      <AuroraRibbon />

      <div className="relative z-10 mx-auto flex w-full max-w-[1280px] flex-1 items-center px-6 py-12 lg:px-10">
        <div className="grid w-full items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <Logo className="mb-8" />
            <div className="ws-badge mb-6">
              <span className="ws-badge-dot" />
              Rentrée 2025-2026
            </div>
            <h1 className="ws-display">
              La gestion scolaire,
              <br />
              centralisée.
            </h1>
            <p className="mt-6 max-w-lg text-[18px] leading-[1.71] tracking-[-0.38px] text-warm-sand">
              Inscriptions, notes, finance et communication pour le Groupe Scolaire Privé Fodeba
              Keita.
            </p>
          </div>

          <div className="ws-card mx-auto w-full max-w-md lg:ml-auto">
            <h2 className="font-display text-[28px] font-light tracking-[-0.56px] text-canvas-white">
              Connexion
            </h2>
            <p className="mt-2 text-[14px] text-silver-mist">
              Identifiants fournis par l&apos;administration
            </p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="ws-label">
                  Adresse e-mail
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="ws-input"
                  placeholder="nom@fodebakeita.gn"
                />
              </div>
              <div>
                <label htmlFor="password" className="ws-label">
                  Mot de passe
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="ws-input"
                />
              </div>

              {error && <div className="ws-error">{error}</div>}

              <button type="submit" disabled={loading} className="ws-btn-primary w-full">
                {loading ? "Connexion en cours" : "Se connecter"}
              </button>
            </form>

            <p className="mt-5 text-center">
              <a href="/forgot-password" className="ws-link">
                Mot de passe oublié
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
