"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { AuroraRibbon } from "@/components/ui/AuroraRibbon";
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
    <div className="relative flex min-h-full flex-1 items-center justify-center overflow-hidden bg-midnight-navy px-6 py-12">
      <AuroraRibbon className="opacity-50" />
      <div className="relative z-10 w-full max-w-md">
        <Logo className="mb-8 justify-center" />
        <div className="ws-card">
          <h1 className="font-display text-[28px] font-light text-canvas-white">Mot de passe oublié</h1>
          <p className="mt-2 text-[14px] text-silver-mist">
            Entrez votre e-mail pour recevoir un lien de réinitialisation.
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
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="ws-input"
              />
            </div>
            {error && <div className="ws-error">{error}</div>}
            {message && (
              <div className="rounded-md border border-silver-mist/25 bg-midnight-navy px-3 py-2 text-[14px] text-warm-sand">
                {message}
              </div>
            )}
            {resetToken && (
              <div className="rounded-md border border-bubblegum/40 bg-lavender-mist/10 px-3 py-2 text-[14px] text-warm-sand">
                <p className="font-medium">Mode développement</p>
                <Link href={`/reset-password?token=${resetToken}`} className="ws-link mt-1 inline-block">
                  Ouvrir la réinitialisation
                </Link>
              </div>
            )}
            <button type="submit" disabled={loading} className="ws-btn-primary w-full">
              {loading ? "Envoi en cours" : "Envoyer le lien"}
            </button>
          </form>
          <p className="mt-6 text-center">
            <Link href="/login" className="ws-link">
              Retour à la connexion
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
