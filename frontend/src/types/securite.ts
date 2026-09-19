export type AuditLog = {
  id: string;
  user_id: string | null;
  user_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
};

export type HistoriqueNote = {
  id: string;
  evaluation_id: string;
  eleve_id: string;
  ancienne_valeur: string | null;
  nouvelle_valeur: string | null;
  created_at: string;
};

export type HistoriquePaiement = {
  id: string;
  paiement_id: string;
  eleve_id: string;
  action: string;
  montant: string;
  statut_avant: string | null;
  statut_apres: string;
  details: string | null;
  created_at: string;
};

export type LoginLog = {
  id: string;
  email: string;
  ip_address: string | null;
  success: boolean;
  created_at: string;
};

export type SauvegardeStatus = {
  repertoire: string;
  derniere_sauvegarde: string | null;
  taille_octets: number | null;
  chiffrement: string;
  procedure_restauration: string;
  https_requis: boolean;
};
