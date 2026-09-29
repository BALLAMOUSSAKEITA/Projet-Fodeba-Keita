"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import { ApiError } from "@/lib/api/client";
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
    <div className="flex min-h-full flex-1 bg-paper">
      <div className="aw-page flex flex-1 items-center py-12 lg:py-16">
        <div className="grid w-full items-center gap-12 lg:grid-cols-2 lg:gap-20">
          <div>
            <Logo className="mb-8" />
            <span className="aw-badge-ember">Rentrée 2025-2026</span>
            <h1 className="aw-display mt-6">
              Gestion scolaire
              <br />
              pour Fodeba Keita
            </h1>
            <p className="mt-6 max-w-md text-[15px] leading-[1.45] text-steel">
              Inscriptions, notes, finance et communication avec les familles. Une plateforme
              claire pour l&apos;équipe pédagogique et administrative.
            </p>
            <div className="mt-8 flex flex-wrap gap-2">
              <span className="aw-badge-tag">Maternelle</span>
              <span className="aw-badge-tag">Primaire</span>
              <span className="aw-badge-tag">Conakry</span>
            </div>
          </div>

          <div className="aw-card mx-auto w-full max-w-md lg:ml-auto">
            <h2 className="aw-heading text-[32px]">Connexion</h2>
            <p className="mt-2 text-[14px] text-steel">Identifiants fournis par l&apos;administration</p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="aw-label">
                  Adresse e-mail
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="aw-input"
                  placeholder="nom@fodebakeita.gn"
                />
              </div>
              <div>
                <label htmlFor="password" className="aw-label">
                  Mot de passe
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="aw-input"
                />
              </div>

              {error && <div className="aw-error">{error}</div>}

              <button type="submit" disabled={loading} className="aw-btn-primary w-full">
                {loading ? "Connexion en cours" : "Se connecter"}
              </button>
            </form>

            <p className="mt-5 text-center">
              <a href="/forgot-password" className="aw-link">
                Mot de passe oublié
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
