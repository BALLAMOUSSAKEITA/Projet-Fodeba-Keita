"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { LogoLight } from "@/components/layout/Logo";

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
    <div className="flex min-h-full flex-1 items-center justify-center bg-slate-50 px-6 py-12">
      <div className="w-full max-w-md">
        <LogoLight className="mb-8 justify-center" />
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
          <h1 className="text-[28px] font-bold text-slate-900">Mot de passe oublié</h1>
          <p className="mt-2 text-[14px] text-slate-500">
            Entrez votre e-mail pour recevoir un lien de réinitialisation.
          </p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label htmlFor="email" className="mb-1.5 block text-[14px] font-medium text-slate-700">
                Adresse e-mail
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-[14px] text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
              />
            </div>
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-[14px] text-red-700">
                {error}
              </div>
            )}
            {message && (
              <div className="rounded-lg border border-teal-200 bg-teal-50 px-4 py-3 text-[14px] text-teal-700">
                {message}
              </div>
            )}
            {resetToken && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-[14px]">
                <p className="font-medium text-amber-800">Mode développement</p>
                <Link href={`/reset-password?token=${resetToken}`} className="mt-1 inline-block text-[14px] font-medium text-teal-600 hover:underline">
                  Ouvrir la réinitialisation
                </Link>
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-teal-600 px-4 py-2.5 text-[14px] font-semibold text-white shadow-sm transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Envoi en cours…" : "Envoyer le lien"}
            </button>
          </form>
          <p className="mt-6 text-center">
            <Link href="/login" className="text-[14px] font-medium text-teal-600 hover:underline">
              ← Retour à la connexion
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
