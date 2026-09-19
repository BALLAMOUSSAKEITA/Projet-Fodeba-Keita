export interface PeriodePaie {
  id: string;
  annee: number;
  mois: number;
  libelle: string;
  statut: string;
}

export interface BulletinPaie {
  id: string;
  personnel_id: string;
  personnel_matricule: string;
  personnel_nom: string;
  personnel_prenoms: string;
  periode_paie_id: string;
  periode_libelle: string;
  salaire_base: number;
  prime_anciennete: number;
  prime_autre: number;
  indemnite_transport: number;
  indemnite_logement: number;
  retenue_cnss: number;
  retenue_its: number;
  retenue_absences: number;
  retenue_avances: number;
  autres_retenues: number;
  brut: number;
  net_a_payer: number;
  jours_absence: number;
  statut: string;
}

export interface MasseSalariale {
  periode_paie_id: string;
  periode_libelle: string;
  nombre_bulletins: number;
  total_brut: number;
  total_net: number;
  total_cnss: number;
  total_its: number;
  total_paye: number;
  total_a_payer: number;
  bulletins: BulletinPaie[];
}

export interface AvanceSalaire {
  id: string;
  personnel_id: string;
  personnel_nom: string;
  personnel_prenoms: string;
  montant: number;
  date_avance: string;
  motif: string | null;
  statut: string;
}
