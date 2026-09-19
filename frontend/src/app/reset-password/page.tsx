"use client";

import { FormEvent, Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { resetPassword } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
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
    return (
      <div className="rounded-[6px] border border-red-200 bg-red-50 px-3 py-2 text-[14px] text-red-700">
        Lien invalide. Demandez un nouveau lien de réinitialisation.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label htmlFor="password" className="sgep-label">
          Nouveau mot de passe
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="sgep-input"
        />
      </div>
      <div>
        <label htmlFor="confirm" className="sgep-label">
          Confirmer le mot de passe
        </label>
        <input
          id="confirm"
          type="password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="sgep-input"
        />
      </div>

      {error && (
        <div className="rounded-[6px] border border-red-200 bg-red-50 px-3 py-2 text-[14px] text-red-700">
          {error}
        </div>
      )}

      <button type="submit" disabled={loading} className="sgep-btn-primary w-full">
        {loading ? "Enregistrement en cours" : "Réinitialiser le mot de passe"}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-full flex-1 items-center justify-center bg-drafting-gray px-6 py-12">
      <div className="w-full max-w-md">
        <Logo className="mb-8 justify-center" />
        <div className="sgep-card">
          <h1 className="text-[24px] font-semibold text-graphite-ink">Nouveau mot de passe</h1>
          <p className="mt-2 text-[14px] text-steel">
            Choisissez un mot de passe d&apos;au moins 8 caractères.
          </p>

          <div className="mt-6">
            <Suspense fallback={<p className="text-[14px] text-steel">Chargement</p>}>
              <ResetPasswordForm />
            </Suspense>
          </div>

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
