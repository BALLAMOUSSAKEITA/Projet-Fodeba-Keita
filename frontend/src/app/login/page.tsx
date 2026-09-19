"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import { ApiError } from "@/lib/api/client";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@fodebakeita.gn");
  const [password, setPassword] = useState("admin123");
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
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Impossible de se connecter. Vérifiez que l'API est démarrée.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-1 flex-col bg-drafting-gray">
      <AnnouncementBar />

      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="sgep-page-container grid w-full items-center gap-16 lg:grid-cols-2">
          <div className="hidden lg:block">
            <p className="text-[13px] font-semibold uppercase tracking-wider text-graphite-ink">
              SGEP
            </p>
            <h1 className="sgep-display mt-4">
              Gérez votre
              <br />
              école.
            </h1>
            <p className="sgep-subtext mt-6 max-w-md">
              Plateforme de gestion scolaire pour le Groupe Scolaire Privé Fodeba Keita —
              inscriptions, notes, finance et communication.
            </p>
          </div>

          <div className="sgep-card mx-auto w-full max-w-md">
            <div className="mb-8">
              <p className="text-[13px] font-semibold uppercase tracking-wider text-graphite-ink lg:hidden">
                SGEP
              </p>
              <h2 className="mt-2 text-[24px] font-semibold leading-snug text-graphite-ink">
                Connexion
              </h2>
              <p className="mt-2 text-[14px] text-steel">
                Groupe Scolaire Privé Fodeba Keita
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="sgep-label">
                  Adresse e-mail
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="sgep-input"
                  placeholder="admin@fodebakeita.gn"
                />
              </div>

              <div>
                <label htmlFor="password" className="sgep-label">
                  Mot de passe
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="sgep-input"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <div className="rounded-[6px] border border-red-200 bg-red-50 px-3 py-2 text-[14px] text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="sgep-btn-primary w-full"
              >
                {loading ? "Connexion..." : "Se connecter"}
              </button>
            </form>

            <p className="mt-5 text-center text-[14px]">
              <a
                href="/forgot-password"
                className="text-graphite-ink underline underline-offset-2 hover:opacity-80"
              >
                Mot de passe oublié ?
              </a>
            </p>

            <p className="mt-4 text-center text-[13px] text-ash">
              Compte de démo : admin@fodebakeita.gn / admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
