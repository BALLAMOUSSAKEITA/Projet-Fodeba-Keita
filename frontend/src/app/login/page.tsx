"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import { ApiError } from "@/lib/api/client";
import { Logo } from "@/components/layout/Logo";
import { LoginPreview } from "@/components/layout/LoginPreview";

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
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Connexion impossible. Vérifiez votre réseau et que le serveur est actif.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-1 bg-drafting-gray">
      <div className="sgep-page-container flex w-full items-center py-10 lg:py-16">
        <div className="grid w-full items-center gap-10 lg:grid-cols-2 lg:gap-16">
          <div className="mx-auto w-full max-w-md lg:mx-0">
            <Logo className="mb-8" />
            <h1 className="text-[32px] font-semibold leading-[1.1] tracking-[-0.03em] text-graphite-ink lg:text-[40px]">
              Espace de gestion scolaire
            </h1>
            <p className="mt-4 max-w-md text-[16px] leading-relaxed text-steel">
              Accédez aux inscriptions, aux notes, à la finance et à la communication avec les
              familles du Groupe Scolaire Privé Fodeba Keita.
            </p>

            <div className="sgep-card mt-8">
              <h2 className="text-[20px] font-semibold text-graphite-ink">Connexion</h2>
              <p className="mt-1 text-[14px] text-steel">Identifiants fournis par l&apos;administration</p>

              <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                <div>
                  <label htmlFor="email" className="sgep-label">
                    Adresse e-mail
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="sgep-input"
                    placeholder="nom@fodebakeita.gn"
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
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="sgep-input"
                  />
                </div>

                {error && (
                  <div className="rounded-[6px] border border-red-200 bg-red-50 px-3 py-2 text-[14px] text-red-700">
                    {error}
                  </div>
                )}

                <button type="submit" disabled={loading} className="sgep-btn-primary w-full">
                  {loading ? "Connexion en cours" : "Se connecter"}
                </button>
              </form>

              <p className="mt-5 text-center text-[14px]">
                <a
                  href="/forgot-password"
                  className="text-graphite-ink underline underline-offset-2 hover:opacity-80"
                >
                  Mot de passe oublié
                </a>
              </p>
            </div>
          </div>

          <LoginPreview />
        </div>
      </div>
    </div>
  );
}
