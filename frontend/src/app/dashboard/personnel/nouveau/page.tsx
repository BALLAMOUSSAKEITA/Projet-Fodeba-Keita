"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createPersonnel } from "@/lib/api/personnel";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";

export default function NouveauPersonnelPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    nom: "",
    prenoms: "",
    sexe: "M",
    telephone: "",
    email: "",
    categorie: "enseignant",
    fonction: "",
    specialite: "",
    date_embauche: "",
  });

  if (!hasPermission("personnel.manage")) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Permission insuffisante.
      </div>
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const p = await createPersonnel(token, {
        ...form,
        email: form.email || undefined,
        fonction: form.categorie === "non_enseignant" ? form.fonction : undefined,
        specialite: form.categorie === "enseignant" ? form.specialite : undefined,
        date_embauche: form.date_embauche || undefined,
      });
      router.push(`/dashboard/personnel/${p.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <Link href="/dashboard/personnel" className="text-sm text-emerald-700 hover:underline">
          ← Retour à l&apos;annuaire
        </Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Ajouter un membre du personnel</h2>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Nom *" value={form.nom} onChange={(v) => setForm({ ...form, nom: v })} required />
          <Field label="Prénoms *" value={form.prenoms} onChange={(v) => setForm({ ...form, prenoms: v })} required />
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Catégorie *</label>
            <select
              value={form.categorie}
              onChange={(e) => setForm({ ...form, categorie: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="enseignant">Enseignant</option>
              <option value="non_enseignant">Non enseignant</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Sexe *</label>
            <select
              value={form.sexe}
              onChange={(e) => setForm({ ...form, sexe: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="M">Homme</option>
              <option value="F">Femme</option>
            </select>
          </div>
          <Field label="Téléphone *" value={form.telephone} onChange={(v) => setForm({ ...form, telephone: v })} required />
          <Field label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} />
          {form.categorie === "enseignant" ? (
            <Field label="Spécialité" value={form.specialite} onChange={(v) => setForm({ ...form, specialite: v })} />
          ) : (
            <Field label="Fonction *" value={form.fonction} onChange={(v) => setForm({ ...form, fonction: v })} required />
          )}
          <Field label="Date d'embauche" type="date" value={form.date_embauche} onChange={(v) => setForm({ ...form, date_embauche: v })} />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-700 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {loading ? "Enregistrement..." : "Enregistrer"}
        </button>
      </form>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
    </div>
  );
}
