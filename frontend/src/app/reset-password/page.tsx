"use client";

import { FormEvent, Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { resetPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { AuroraRibbon } from "@/components/ui/AuroraRibbon";
import { Logo } from "@/components/layout/Logo";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    if (password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères");
      return;
    }
    setLoading(true);
    try {
      await resetPassword(token, password);
      router.push("/login?reset=success");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur lors de la réinitialisation");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return <div className="ws-error">Lien invalide. Demandez un nouveau lien.</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label htmlFor="password" className="ws-label">
          Nouveau mot de passe
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="ws-input"
        />
      </div>
      <div>
        <label htmlFor="confirm" className="ws-label">
          Confirmer le mot de passe
        </label>
        <input
          id="confirm"
          type="password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="ws-input"
        />
      </div>
      {error && <div className="ws-error">{error}</div>}
      <button type="submit" disabled={loading} className="ws-btn-primary w-full">
        {loading ? "Enregistrement en cours" : "Réinitialiser le mot de passe"}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="relative flex min-h-full flex-1 items-center justify-center overflow-hidden bg-midnight-navy px-6 py-12">
      <AuroraRibbon className="opacity-50" />
      <div className="relative z-10 w-full max-w-md">
        <Logo className="mb-8 justify-center" />
        <div className="ws-card">
          <h1 className="font-display text-[28px] font-light text-canvas-white">Nouveau mot de passe</h1>
          <p className="mt-2 text-[14px] text-silver-mist">Minimum 8 caractères.</p>
          <div className="mt-6">
            <Suspense fallback={<p className="text-silver-mist">Chargement</p>}>
              <ResetPasswordForm />
            </Suspense>
          </div>
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
