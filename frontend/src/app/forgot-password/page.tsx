"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setResetToken(null);
    setLoading(true);

    try {
      const response = await forgotPassword(email);
      setMessage(response.message);
      if (response.reset_token) {
        setResetToken(response.reset_token);
      }
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible d'envoyer la demande. Vérifiez que l'API est démarrée.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-1 flex-col bg-drafting-gray">
      <AnnouncementBar />

      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="sgep-card mx-auto w-full max-w-md">
          <h1 className="text-[24px] font-semibold text-graphite-ink">Mot de passe oublié</h1>
          <p className="mt-2 text-[14px] text-steel">
            Saisissez votre e-mail pour recevoir un lien de réinitialisation.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
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
              />
            </div>

            {error && (
              <div className="rounded-[6px] border border-red-200 bg-red-50 px-3 py-2 text-[14px] text-red-700">
                {error}
              </div>
            )}
            {message && (
              <div className="rounded-[6px] border border-hairline bg-drafting-gray px-3 py-2 text-[14px] text-graphite-ink">
                {message}
              </div>
            )}
            {resetToken && (
              <div className="rounded-[6px] border border-amber-200 bg-amber-50 px-3 py-2 text-[14px] text-amber-900">
                <p className="font-medium">Mode développement</p>
                <Link
                  href={`/reset-password?token=${resetToken}`}
                  className="mt-1 block break-all text-graphite-ink underline underline-offset-2"
                >
                  Cliquez ici pour réinitialiser votre mot de passe
                </Link>
              </div>
            )}

            <button type="submit" disabled={loading} className="sgep-btn-primary w-full">
              {loading ? "Envoi..." : "Envoyer le lien"}
            </button>
          </form>

          <p className="mt-6 text-center text-[14px]">
            <Link
              href="/login"
              className="text-graphite-ink underline underline-offset-2 hover:opacity-80"
            >
              Retour à la connexion
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
