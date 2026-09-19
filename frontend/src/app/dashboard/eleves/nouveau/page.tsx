"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createEleve } from "@/lib/api/eleves";
import { listNiveaux } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import type { Niveau } from "@/types/parametrage";

const EMPTY_TUTEUR = {
  type: "pere",
  nom: "",
  prenoms: "",
  telephone: "",
  profession: "",
};

export default function NouvelElevePage() {
  const router = useRouter();
  const [niveaux, setNiveaux] = useState<Niveau[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    nom: "",
    prenoms: "",
    sexe: "M",
    date_naissance: "",
    lieu_naissance: "",
    nationalite: "Guinéenne",
    adresse: "",
    groupe_sanguin: "",
    allergies: "",
    niveau_id: "",
  });
  const [tuteurs, setTuteurs] = useState([{ ...EMPTY_TUTEUR }]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    listNiveaux(token).then((data) => {
      setNiveaux(data);
      if (data.length > 0) setForm((f) => ({ ...f, niveau_id: data[0].id }));
    });
  }, []);

  if (!hasPermission("students.enroll")) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Permission insuffisante pour inscrire un élève.
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
      const eleve = await createEleve(token, {
        ...form,
        tuteurs: tuteurs.filter((t) => t.nom && t.telephone),
      });
      router.push(`/dashboard/eleves/${eleve.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link href="/dashboard/eleves" className="text-sm text-emerald-700 hover:underline">
          ← Retour à la liste
        </Link>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Inscrire un nouvel élève</h2>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Identité de l&apos;élève</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Nom *" value={form.nom} onChange={(v) => setForm({ ...form, nom: v })} required />
            <Field label="Prénoms *" value={form.prenoms} onChange={(v) => setForm({ ...form, prenoms: v })} required />
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Sexe *</label>
              <select
                value={form.sexe}
                onChange={(e) => setForm({ ...form, sexe: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                required
              >
                <option value="M">Garçon</option>
                <option value="F">Fille</option>
              </select>
            </div>
            <Field label="Date de naissance *" type="date" value={form.date_naissance} onChange={(v) => setForm({ ...form, date_naissance: v })} required />
            <Field label="Lieu de naissance" value={form.lieu_naissance} onChange={(v) => setForm({ ...form, lieu_naissance: v })} />
            <Field label="Nationalité" value={form.nationalite} onChange={(v) => setForm({ ...form, nationalite: v })} />
            <Field label="Adresse" value={form.adresse} onChange={(v) => setForm({ ...form, adresse: v })} />
            <Field label="Groupe sanguin" value={form.groupe_sanguin} onChange={(v) => setForm({ ...form, groupe_sanguin: v })} />
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Allergies</label>
              <textarea
                value={form.allergies}
                onChange={(e) => setForm({ ...form, allergies: e.target.value })}
                rows={2}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Niveau *</label>
              <select
                value={form.niveau_id}
                onChange={(e) => setForm({ ...form, niveau_id: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                required
              >
                {niveaux.map((n) => (
                  <option key={n.id} value={n.id}>{n.libelle}</option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Tuteurs / Responsables</h3>
          {tuteurs.map((t, i) => (
            <div key={i} className="mb-4 grid gap-3 rounded-lg bg-slate-50 p-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Lien</label>
                <select
                  value={t.type}
                  onChange={(e) => {
                    const copy = [...tuteurs];
                    copy[i] = { ...copy[i], type: e.target.value };
                    setTuteurs(copy);
                  }}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="pere">Père</option>
                  <option value="mere">Mère</option>
                  <option value="tuteur">Tuteur légal</option>
                </select>
              </div>
              <Field label="Nom *" value={t.nom} onChange={(v) => { const c = [...tuteurs]; c[i] = { ...c[i], nom: v }; setTuteurs(c); }} />
              <Field label="Prénoms *" value={t.prenoms} onChange={(v) => { const c = [...tuteurs]; c[i] = { ...c[i], prenoms: v }; setTuteurs(c); }} />
              <Field label="Téléphone *" value={t.telephone} onChange={(v) => { const c = [...tuteurs]; c[i] = { ...c[i], telephone: v }; setTuteurs(c); }} />
              <Field label="Profession" value={t.profession} onChange={(v) => { const c = [...tuteurs]; c[i] = { ...c[i], profession: v }; setTuteurs(c); }} />
            </div>
          ))}
          <button
            type="button"
            onClick={() => setTuteurs([...tuteurs, { ...EMPTY_TUTEUR }])}
            className="text-sm text-emerald-700 hover:underline"
          >
            + Ajouter un tuteur
          </button>
        </section>

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-700 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
        >
          {loading ? "Inscription..." : "Inscrire l'élève"}
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
  required,
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
