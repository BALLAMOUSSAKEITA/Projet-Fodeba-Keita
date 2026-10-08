"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createTransfertEntrant } from "@/lib/api/eleves";
import { listClasses } from "@/lib/api/parametrage";
import { ApiError } from "@/lib/api/client";
import { getToken, hasPermission } from "@/lib/auth/session";
import { useAnneeScolaire } from "@/components/layout/AnneeScolaireProvider";
import type { TransfertEntrantRequest } from "@/types/eleve";
import type { Classe } from "@/types/parametrage";

const EMPTY_TUTEUR = {
  type: "pere",
  nom: "",
  prenoms: "",
  telephone: "",
  profession: "",
};

function optionalField(value: string): string | undefined {
  const v = value.trim();
  return v || undefined;
}

export default function TransfertEntrantPage() {
  const router = useRouter();
  const { anneeId } = useAnneeScolaire();
  const [classes, setClasses] = useState<Classe[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    nom: "",
    prenoms: "",
    sexe: "",
    date_naissance: "",
    lieu_naissance: "",
    nationalite: "",
    adresse: "",
    classe_id: "",
    ecole_origine: "",
    date_transfert: "",
    observations: "",
  });
  const [tuteurs, setTuteurs] = useState([{ ...EMPTY_TUTEUR }]);

  useEffect(() => {
    const token = getToken();
    if (!token || !anneeId) return;
    listClasses(token, anneeId).then(setClasses).catch(() => {});
  }, [anneeId]);

  if (!hasPermission("students.enroll")) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Permission insuffisante pour enregistrer un transfert entrant.
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
      const payload: TransfertEntrantRequest = {
        nom: optionalField(form.nom),
        prenoms: optionalField(form.prenoms),
        sexe: form.sexe === "M" || form.sexe === "F" ? form.sexe : undefined,
        date_naissance: form.date_naissance || undefined,
        lieu_naissance: optionalField(form.lieu_naissance),
        nationalite: optionalField(form.nationalite),
        adresse: optionalField(form.adresse),
        classe_id: form.classe_id || undefined,
        ecole_origine: optionalField(form.ecole_origine),
        date_transfert: form.date_transfert || undefined,
        observations: optionalField(form.observations),
        tuteurs: tuteurs
          .map((t) => ({
            type: t.type,
            nom: optionalField(t.nom),
            prenoms: optionalField(t.prenoms),
            telephone: optionalField(t.telephone),
            profession: optionalField(t.profession),
          }))
          .filter((t) => t.nom || t.prenoms || t.telephone || t.profession),
      };
      const eleve = await createTransfertEntrant(token, payload);
      router.push(`/dashboard/eleves/${eleve.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur lors du transfert");
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
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Transfert entrant</h2>
        <p className="text-sm text-slate-500">Inscrire un élève provenant d&apos;une autre école — champs facultatifs.</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">École d&apos;origine</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label="École d'origine"
              value={form.ecole_origine}
              onChange={(v) => setForm({ ...form, ecole_origine: v })}
            />
            <Field
              label="Date du transfert"
              type="date"
              value={form.date_transfert}
              onChange={(v) => setForm({ ...form, date_transfert: v })}
            />
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Observations</label>
              <textarea
                value={form.observations}
                onChange={(e) => setForm({ ...form, observations: e.target.value })}
                rows={2}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Identité de l&apos;élève</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Nom" value={form.nom} onChange={(v) => setForm({ ...form, nom: v })} />
            <Field label="Prénoms" value={form.prenoms} onChange={(v) => setForm({ ...form, prenoms: v })} />
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Sexe</label>
              <select
                value={form.sexe}
                onChange={(e) => setForm({ ...form, sexe: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">—</option>
                <option value="M">Garçon</option>
                <option value="F">Fille</option>
              </select>
            </div>
            <Field
              label="Date de naissance"
              type="date"
              value={form.date_naissance}
              onChange={(v) => setForm({ ...form, date_naissance: v })}
            />
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Classe</label>
              <select
                value={form.classe_id}
                onChange={(e) => setForm({ ...form, classe_id: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">— Aucune pour l&apos;instant —</option>
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nom}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-semibold text-slate-900">Tuteur principal</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label="Nom"
              value={tuteurs[0].nom}
              onChange={(v) => setTuteurs([{ ...tuteurs[0], nom: v }])}
            />
            <Field
              label="Prénoms"
              value={tuteurs[0].prenoms}
              onChange={(v) => setTuteurs([{ ...tuteurs[0], prenoms: v }])}
            />
            <Field
              label="Téléphone"
              value={tuteurs[0].telephone}
              onChange={(v) => setTuteurs([{ ...tuteurs[0], telephone: v }])}
            />
          </div>
        </section>

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-700 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {loading ? "Enregistrement..." : "Enregistrer le transfert entrant"}
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
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
    </div>
  );
}
