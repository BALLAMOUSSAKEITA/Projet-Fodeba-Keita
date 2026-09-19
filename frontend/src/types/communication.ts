export type Annonce = {
  id: string;
  titre: string;
  contenu: string;
  audience: string;
  statut: string;
  date_publication: string | null;
  date_expiration: string | null;
  auteur_nom: string | null;
};

export type ModeleMessage = {
  id: string;
  code: string;
  libelle: string;
  sujet: string;
  corps: string;
  canal: string;
  actif: boolean;
};

export type HistoriqueCommunication = {
  id: string;
  canal: string;
  destinataire: string;
  sujet: string;
  corps: string;
  statut: string;
  envoye_le: string | null;
  eleve_id: string | null;
};

export type EnfantItem = {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  classe_nom: string | null;
};

export type PortailResume = {
  eleve_id: string;
  matricule: string;
  nom: string;
  prenoms: string;
  classe_nom: string | null;
  annee_libelle: string;
  total_du: string;
  total_paye: string;
  total_restant: string;
  jours_absents: number;
  absences_non_justifiees: number;
  jours_retards: number;
  incidents_count: number;
  periodes_notes: {
    periode_id: string;
    periode_libelle: string;
    moyenne_generale: string | null;
    rang: number | null;
  }[];
  annonces: Annonce[];
};
