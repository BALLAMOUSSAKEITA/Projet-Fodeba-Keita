"use client";

import { useRef } from "react";
import {
  ETABLISSEMENT_ADRESSE,
  ETABLISSEMENT_NOM,
  ETABLISSEMENT_TELEPHONE_AFFICHAGE,
  formatTelephoneAffichage,
} from "@/lib/etablissementDefaults";
import type { Paiement } from "@/types/paiements";

const MODES: Record<string, string> = {
  especes: "Espèces",
  orange_money: "Orange Money",
  mtn_momo: "MTN MoMo",
  virement: "Virement",
  cheque: "Chèque",
};

function fmt(n: number) {
  return `${Math.round(n).toLocaleString("fr-FR")} GNF`;
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export function RecuPaiementCard({
  paiement,
  etablissementNom = ETABLISSEMENT_NOM,
  etablissementAdresse = ETABLISSEMENT_ADRESSE,
  etablissementTelephone = ETABLISSEMENT_TELEPHONE_AFFICHAGE,
  anneeLibelle,
  classeNom,
  resteApresPaiement,
  onDownloadPdf,
  downloading,
}: {
  paiement: Paiement;
  etablissementNom?: string;
  etablissementAdresse?: string;
  etablissementTelephone?: string;
  anneeLibelle?: string;
  classeNom?: string;
  resteApresPaiement?: number | null;
  onDownloadPdf: () => void;
  downloading?: boolean;
}) {
  const printRef = useRef<HTMLDivElement>(null);

  function handlePrint() {
    const node = printRef.current;
    if (!node || typeof window === "undefined") return;
    const html = node.outerHTML;
    const w = window.open("", "_blank", "width=720,height=900");
    if (!w) return;
    w.document.write(`<!DOCTYPE html><html><head><title>Reçu ${paiement.numero_recu}</title>
      <style>
        body { font-family: system-ui, sans-serif; margin: 24px; color: #0f172a; }
        .recu { max-width: 420px; margin: 0 auto; border: 2px solid #047857; border-radius: 12px; overflow: hidden; }
        .head { background: #047857; color: #fff; padding: 20px; text-align: center; }
        .head h1 { margin: 0; font-size: 1.05rem; font-weight: 700; }
        .head p { margin: 6px 0 0; font-size: 0.75rem; opacity: 0.9; letter-spacing: 0.04em; text-transform: uppercase; }
        .meta { display: flex; justify-content: space-between; padding: 12px 16px; font-size: 0.8rem; border-bottom: 1px dashed #d1fae5; }
        .body { padding: 16px; }
        .eleve { background: #f0fdf4; border-left: 4px solid #047857; padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 16px; }
        .eleve .label { font-size: 0.65rem; text-transform: uppercase; color: #64748b; }
        .eleve .name { font-size: 1.1rem; font-weight: 700; margin-top: 4px; }
        dl { margin: 0; font-size: 0.85rem; }
        dl div { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
        dl dt { color: #64748b; }
        dl dd { margin: 0; font-weight: 600; text-align: right; }
        .montant { margin-top: 16px; background: #047857; color: #fff; text-align: center; padding: 16px; border-radius: 8px; }
        .montant .lbl { font-size: 0.7rem; opacity: 0.85; text-transform: uppercase; }
        .montant .val { font-size: 1.5rem; font-weight: 800; margin-top: 4px; }
        .foot { padding: 12px 16px; font-size: 0.7rem; color: #64748b; text-align: center; border-top: 1px dashed #d1fae5; }
        .sig { margin-top: 24px; border-top: 1px solid #cbd5e1; padding-top: 8px; font-size: 0.75rem; color: #64748b; }
      </style></head><body>${html}</body></html>`);
    w.document.close();
    w.focus();
    w.print();
  }

  return (
    <div className="space-y-3">
      <div ref={printRef} className="recu overflow-hidden rounded-xl border-2 border-emerald-700 bg-white shadow-md">
        <div className="bg-emerald-700 px-5 py-4 text-center text-white">
          <p className="text-xs font-medium uppercase tracking-wider text-emerald-100">Reçu officiel</p>
          <h3 className="mt-1 text-base font-bold leading-snug">{etablissementNom}</h3>
          <p className="mt-1 text-xs text-emerald-100">{etablissementAdresse}</p>
          <p className="mt-0.5 text-xs text-emerald-100">
            Tél. {formatTelephoneAffichage(etablissementTelephone)}
          </p>
          <p className="mt-0.5 text-xs text-emerald-100">Paiement scolarité</p>
        </div>
        <div className="flex justify-between border-b border-dashed border-emerald-200 px-4 py-2 text-xs text-slate-600">
          <span>{formatDate(paiement.date_paiement)}</span>
          <span className="font-mono font-semibold text-slate-900">{paiement.numero_recu}</span>
        </div>
        <div className="space-y-4 p-4">
          <div className="rounded-r-lg border-l-4 border-emerald-600 bg-emerald-50 px-3 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">Élève</p>
            <p className="text-lg font-bold text-slate-900">
              {paiement.eleve_prenoms} {paiement.eleve_nom}
            </p>
            <p className="text-xs text-slate-600">Matricule {paiement.eleve_matricule}</p>
          </div>
          <dl className="space-y-0 text-sm">
            {anneeLibelle && (
              <div className="flex justify-between border-b border-slate-100 py-2">
                <dt className="text-slate-500">Année scolaire</dt>
                <dd className="font-medium">{anneeLibelle}</dd>
              </div>
            )}
            {classeNom && (
              <div className="flex justify-between border-b border-slate-100 py-2">
                <dt className="text-slate-500">Classe</dt>
                <dd className="font-medium">{classeNom}</dd>
              </div>
            )}
            <div className="flex justify-between border-b border-slate-100 py-2">
              <dt className="text-slate-500">Objet</dt>
              <dd className="font-medium">{paiement.type_frais_libelle}</dd>
            </div>
            <div className="flex justify-between py-2">
              <dt className="text-slate-500">Mode</dt>
              <dd>{MODES[paiement.mode_paiement] ?? paiement.mode_paiement}</dd>
            </div>
          </dl>
          <div className="rounded-lg bg-emerald-700 px-4 py-4 text-center text-white">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-emerald-100">Montant encaissé</p>
            <p className="mt-1 text-2xl font-bold">{fmt(Number(paiement.montant))}</p>
          </div>
          {resteApresPaiement != null && (
            <p className="text-center text-xs text-slate-600">
              Reste à payer après ce versement :{" "}
              <span className="font-semibold text-red-700">{fmt(resteApresPaiement)}</span>
            </p>
          )}
          <div className="sig pt-2 text-center text-xs text-slate-500">
            <p>Signature et cachet — La caisse</p>
            <div className="mx-auto mt-6 h-px w-40 bg-slate-300" />
          </div>
        </div>
        <p className="border-t border-dashed border-emerald-200 px-4 py-2 text-center text-[10px] text-slate-500">
          Conservez ce reçu comme preuve de paiement. Document généré par GSP.
        </p>
      </div>
      <div className="flex flex-wrap gap-2 print:hidden">
        <button
          type="button"
          onClick={onDownloadPdf}
          disabled={downloading}
          className="flex-1 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50"
        >
          {downloading ? "Génération…" : "Télécharger le PDF"}
        </button>
        <button
          type="button"
          onClick={handlePrint}
          className="flex-1 rounded-lg border border-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-800 hover:bg-emerald-50"
        >
          Imprimer le reçu
        </button>
      </div>
    </div>
  );
}
