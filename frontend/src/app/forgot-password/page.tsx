"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { Logo } from "@/components/layout/Logo";

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
      if (response.reset_token) setResetToken(response.reset_token);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Envoi impossible. Vérifiez le réseau et le serveur.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-1 items-center justify-center bg-paper px-6 py-12">
      <div className="w-full max-w-md">
        <Logo className="mb-8 justify-center" />
        <div className="aw-card">
          <h1 className="text-[28px] font-semibold text-obsidian">Mot de passe oublié</h1>
          <p className="mt-2 text-[14px] text-steel">
            Entrez votre e-mail pour recevoir un lien de réinitialisation.
          </p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label htmlFor="email" className="aw-label">
                Adresse e-mail
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="aw-input"
              />
            </div>
            {error && <div className="aw-error">{error}</div>}
            {message && (
              <div className="rounded-[14px] border border-cloud bg-paper px-3 py-2 text-[14px] text-graphite">
                {message}
              </div>
            )}
            {resetToken && (
              <div className="rounded-[14px] border border-cloud bg-paper px-3 py-2 text-[14px]">
                <p className="font-medium text-graphite">Mode développement</p>
                <Link href={`/reset-password?token=${resetToken}`} className="aw-link mt-1 inline-block">
                  Ouvrir la réinitialisation
                </Link>
              </div>
            )}
            <button type="submit" disabled={loading} className="aw-btn-primary w-full">
              {loading ? "Envoi en cours" : "Envoyer le lien"}
            </button>
          </form>
          <p className="mt-6 text-center">
            <Link href="/login" className="aw-link">
              Retour à la connexion
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
