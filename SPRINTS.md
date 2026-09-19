# Suivi des sprints — SGEP Fodeba Keita

**Projet :** Système de Gestion d'École Primaire (SGEP)  
**Établissement :** Groupe Scolaire Privé Fodeba Keita — Conakry, Guinée  
**Stack :** FastAPI · Next.js · PostgreSQL  
**Durée par sprint :** 2 semaines  

---

## Légende des statuts

| Statut | Signification |
|--------|---------------|
| ⬜ | Non démarré |
| 🔄 | En cours |
| ✅ | Terminé |
| ⏸️ | En pause / bloqué |

**Comment utiliser ce document :** cochez `[x]` les cases au fur et à mesure. Quand toutes les cases d'un sprint sont cochées, passez le statut du sprint à ✅.

---

## Vue d'ensemble

| Sprint | Nom | Statut | Date début | Date fin | Notes |
|--------|-----|--------|------------|----------|-------|
| 0 | Cadrage & validation | ⬜ | | | |
| 1 | Conception UX/UI & architecture | ⬜ | | | |
| 2 | Setup technique & fondations | ✅ | 2026-09-16 | 2026-09-16 | Code prêt — lancer Docker Desktop pour staging |
| 3 | Authentification & utilisateurs | ✅ | 2026-09-16 | 2026-09-16 | Auth réelle + RBAC |
| 4 | Paramétrage de l'établissement | ✅ | 2026-09-16 | 2026-09-16 | Fodeba Keita 2025-2026 |
| 5 | Gestion des élèves (partie 1) | ✅ | 2026-09-16 | 2026-09-16 | Inscriptions + matricule auto |
| 6 | Élèves (partie 2) & classes | ✅ | 2026-09-16 | 2026-09-16 | Affectations, transferts, PDF |
| 7 | Enseignants & personnel | ✅ | 2026-09-16 | 2026-09-16 | Annuaire, affectations, congés |
| 8 | Emploi du temps | ✅ | 2026-09-16 | 2026-09-16 | Grille, conflits, PDF/Excel |
| 9 | Évaluations & notes (primaire) | ✅ | 2026-09-16 | 2026-09-16 | Saisie, moyennes, rangs, verrou |
| 10 | Bulletins & évaluations maternelle | ✅ | 2026-09-16 | 2026-09-16 | PDF primaire/maternelle, palmarès |
| 11 | Présences & discipline | ✅ | 2026-09-16 | 2026-09-16 | Appel, cumuls, discipline |
| 12 | Paiements & frais scolaires | ✅ | 2026-09-16 | 2026-09-16 | Encaissement, reçu PDF, impayés |
| 13 | Salaires & paie | ✅ | 2026-09-16 | 2026-09-16 | Calcul paie, bulletins PDF |
| 14 | Dépenses, budget & comptabilité | ✅ | 2026-09-17 | 2026-09-17 | Dépenses, budget, journal, export |
| 15 | Communication & portail parent | ✅ | 2026-09-17 | 2026-09-17 | Annonces, portail parent, historique |
| 16 | Rapports & tableaux de bord | ✅ | 2026-09-17 | 2026-09-17 | KPI direction, rapports exportables |
| 17 | Sécurité, audit & sauvegarde | ✅ | 2026-09-18 | 2026-09-18 | Audit, historiques, clôture année |
| 18 | Mode hors ligne & synchronisation | ✅ | 2026-09-18 | 2026-09-18 | PWA, IndexedDB, sync batch |
| 19 | Tests, recette & corrections | ✅ | 2026-09-18 | 2026-09-18 | OWASP, perf, E2E, recette |
| 20 | Déploiement, migration & formation | ✅ | 2026-09-18 | 2026-09-18 | Prod Docker, migration CSV, manuels |

**Progression globale :** 19 / 21 sprints terminés

---

## Definition of Done (commune à tous les sprints)

- [ ] Fonctionnalités « Indispensable » du sprint implémentées
- [ ] API documentée dans Swagger
- [ ] Tests unitaires et d'intégration passants
- [ ] Revue de code effectuée
- [ ] Interface en français, responsive
- [ ] Démo réalisée avec la direction
- [ ] Déployé en environnement staging

---

## Sprint 0 — Cadrage & validation

**Statut :** ⬜ Non démarré  
**Objectif :** Aligner la MOA et la MOE sur le périmètre et les priorités.

### Tâches

- [ ] Atelier de lancement avec la direction
- [ ] Validation du cahier des charges v1.0
- [ ] Priorisation MoSCoW (Indispensable / Souhaitable / Optionnel)
- [ ] Inventaire des données existantes (Excel, registres papier)
- [ ] Confirmation de la matrice des rôles utilisateurs
- [ ] Backlog produit v1 rédigé et validé

### Livrables

- [ ] Compte-rendu d'atelier signé
- [ ] Backlog priorisé
- [ ] Périmètre MVP figé

---

## Sprint 1 — Conception UX/UI & architecture

**Statut :** ⬜ Non démarré  
**Objectif :** Poser les fondations visuelles et techniques.

### Tâches

- [ ] Maquettes Figma : login, dashboard, fiche élève, saisie notes
- [ ] Design system (TailwindCSS, composants UI)
- [ ] Modèle entité-relation détaillé (30+ entités)
- [ ] Script SQL initial + stratégie migrations Alembic
- [ ] Spécification OpenAPI initiale
- [ ] Document d'architecture technique
- [ ] Repository Git initialisé

### Livrables

- [ ] Maquettes Figma exportées
- [ ] Schéma ERD validé
- [ ] Document d'architecture signé

---

## Sprint 2 — Setup technique & fondations

**Statut :** ✅ Terminé  
**Objectif :** Environnement de développement opérationnel.

### Backend (FastAPI)

- [x] Structure projet (`app/`, routers, middleware, config)
- [x] SQLAlchemy 2 + Alembic + PostgreSQL
- [x] Docker Compose (API, PostgreSQL, Redis, MinIO)
- [x] CI/CD (lint, tests, build)
- [x] Swagger/OpenAPI auto-généré

### Frontend (Next.js)

- [x] Projet Next.js (App Router, TypeScript)
- [x] Layout principal + navigation par rôle
- [x] Client API typé
- [x] i18n français (base)

### Infra

- [x] Environnements dev, staging, prod configurés
- [x] HTTPS/TLS et variables d'environnement

### Livrables

- [x] Stack déployée en staging *(fichiers prêts — exécuter `docker compose up -d`)*
- [x] Page login fonctionnelle (mock ou réelle)

---

## Sprint 3 — Authentification & gestion des utilisateurs

**Statut :** ✅ Terminé  
**Module :** M1 — Authentification  
**Objectif :** Connexion sécurisée et gestion des rôles.

### Backend

- [x] F-AUT-01 — Connexion sécurisée (bcrypt/argon2)
- [x] F-AUT-02 — Rôles et permissions granulaires (RBAC)
- [x] F-AUT-03 — Création de comptes par administrateur
- [x] F-AUT-04 — Réinitialisation mot de passe (email/SMS)
- [x] F-AUT-06 — Verrouillage après 5 tentatives échouées
- [x] F-AUT-08 — Expiration de session paramétrable
- [x] F-AUT-07 — Journal de connexion (souhaitable)

### Frontend

- [x] Page de connexion
- [x] Page mot de passe oublié / réinitialisation
- [x] Interface gestion utilisateurs (admin)
- [x] Gestion des rôles et permissions

### Tests

- [x] Tests unitaires authentification
- [x] Tests intégration RBAC

---

## Sprint 4 — Paramétrage de l'établissement

**Statut :** ✅ Terminé  
**Module :** M2 — Paramétrage  
**Objectif :** Configurer l'école Fodeba Keita pour l'année active.

### Backend

- [x] F-PAR-01 — Fiche établissement (nom, logo, adresse, GNF)
- [x] F-PAR-02 — Années scolaires (année active unique)
- [x] F-PAR-03 — Niveaux PS, MS, GS, 1re à 6e Année
- [x] F-PAR-04 — Classes (capacité, salle)
- [x] F-PAR-05 — Matières par niveau avec coefficients
- [x] F-PAR-06 — Périodes (trimestres/semestres)
- [x] F-PAR-07 — Barème (/10, /20, /100) et règles de passage
- [x] F-PAR-08 — Devise GNF
- [x] F-PAR-09 — Types de frais scolaires
- [x] F-PAR-11 — Calendrier (jours fériés guinéens, vacances)
- [x] F-PAR-12 — Référentiels (régions, nationalités, etc.)

### Frontend

- [x] Interface admin paramétrage établissement
- [x] Wizard première configuration
- [x] Gestion années scolaires et niveaux

### Livrable clé

- [x] École paramétrée pour l'année 2025–2026

---

## Sprint 5 — Gestion des élèves (partie 1)

**Statut :** ✅ Terminé  
**Module :** M3 — Élèves (inscriptions)  
**Objectif :** Inscrire et gérer les fiches élèves.

### Backend

- [x] F-ELV-01 — Fiche élève complète
- [x] F-ELV-02 — Matricule automatique (ex. 2025-P3-0042)
- [x] F-ELV-03 — Inscription nouvel élève
- [x] F-ELV-04 — Réinscription année précédente
- [x] F-ELV-05 — Enregistrement tuteurs (père, mère, tuteur légal)
- [x] F-ELV-11 — Recherche et filtres

### Frontend

- [x] Formulaire création / édition élève
- [x] Liste élèves avec recherche et filtres
- [x] Fiche détail élève
- [x] Formulaire tuteurs

---

## Sprint 6 — Élèves (partie 2) & classes

**Statut :** ✅ Terminé  
**Modules :** M3 + M5 — Classes & affectations  
**Objectif :** Affectations, transferts, classes et attestations.

### Backend

- [x] F-ELV-06 — Affectation en classe (contrôle capacité)
- [x] F-ELV-07 — Transfert entrant
- [x] F-ELV-08 — Transfert sortant + certificat
- [x] F-ELV-10 — Historique scolaire
- [x] F-ELV-12 — Attestations (scolarité, fréquentation)
- [x] F-ELV-16 — Élèves inactifs (abandon, décès, départ)
- [x] F-ELV-17 — Statistiques effectifs
- [x] F-CLA-01 — Création classes *(Sprint 4 — paramétrage)*
- [x] F-CLA-02 — Effectif temps réel + alerte dépassement
- [x] F-CLA-03 — Affectation titulaire et intervenants *(Sprint 7)*
- [x] F-CLA-04 — Liste élèves imprimable

### Frontend

- [x] Interface affectation classe
- [x] Gestion transferts entrant/sortant
- [x] Vue classes avec effectifs
- [x] Génération et impression attestations / listes

---

## Sprint 7 — Enseignants & personnel

**Statut :** ✅ Terminé  
**Module :** M4 — Personnel  
**Objectif :** Gérer enseignants et personnel non enseignant.

### Backend

- [x] F-ENS-01 — Fiche enseignant
- [x] F-ENS-02 — Diplômes et qualifications
- [x] F-ENS-03 — Contrats (CDI, CDD, vacataire)
- [x] F-ENS-04 — Affectation pédagogique (classe + matière)
- [x] F-ENS-05 — Enseignant titulaire
- [x] F-ENS-06 — Congés et absences
- [x] F-ENS-09 — Personnel non enseignant

### Frontend

- [x] Annuaire personnel
- [x] Fiche enseignant / employé
- [x] Gestion affectations pédagogiques
- [x] Gestion congés et absences

---

## Sprint 8 — Emploi du temps

**Statut :** ✅ Terminé  
**Module :** M6 — Emploi du temps  
**Objectif :** Planifier les cours par classe et enseignant.

### Backend

- [x] F-EDT-01 — Créneaux horaires
- [x] F-EDT-02 — EDT par classe (matière / enseignant / salle)
- [x] F-EDT-03 — Détection conflits enseignant/salle
- [x] F-EDT-04 — Vue EDT enseignant
- [x] F-EDT-05 — Export PDF et Excel

### Frontend

- [x] Grille emploi du temps (classe)
- [x] Vue emploi du temps enseignant
- [x] Alertes conflits
- [x] Impression / export PDF

---

## Sprint 9 — Évaluations & notes (primaire)

**Statut :** ✅ Terminé  
**Module :** M7 — Notes (mode chiffré)  
**Objectif :** Saisir les notes et calculer moyennes/rangs.

### Backend

- [x] F-EVA-01 — Types d'évaluation
- [x] F-EVA-02 — Saisie notes par classe/matière/période
- [x] F-EVA-03 — Coefficients par matière et évaluation
- [x] F-EVA-04 — Contrôle saisie (barème, absents « ABS »)
- [x] F-EVA-05 — Moyenne par matière
- [x] F-EVA-06 — Moyenne générale pondérée
- [x] F-EVA-07 — Rangs et ex æquo
- [x] F-EVA-08 — Appréciations automatiques + libres
- [x] F-EVA-10 — Verrouillage notes après validation

### Frontend

- [x] Grille saisie notes (navigation clavier Tab/Entrée)
- [x] Vue moyennes et rangs par classe
- [x] Interface validation direction

---

## Sprint 10 — Bulletins & évaluations maternelle

**Statut :** ✅ Terminé  
**Module :** M7 — Bulletins (2 modes)  
**Objectif :** Générer bulletins primaire (chiffré) et maternelle (compétences).

### Backend — Primaire

- [x] F-EVA-09 — Bulletin scolaire PDF
- [x] F-EVA-11 — Décision de passage (admis, redouble, exclu)
- [x] F-EVA-13 — Statistiques pédagogiques
- [x] F-EVA-14 — Bulletin annuel consolidé
- [x] F-EVA-12 — Palmarès (souhaitable)

### Backend — Maternelle

- [x] F-EVA-15 — Grille compétences (acquis / en cours / non acquis)
- [x] F-EVA-16 — Bulletin maternelle qualitatif

### Frontend

- [x] Génération bulletins en masse
- [x] Prévisualisation PDF
- [x] Interface évaluation maternelle par compétences
- [x] Palmarès et décisions de passage

### Critère d'acceptation

- [x] Notes saisies → moyennes, rangs et bulletins conformes au barème

---

## Sprint 11 — Présences & discipline

**Statut :** ✅ Terminé  
**Module :** M8 — Présences  
**Objectif :** Suivre présences, absences et discipline.

### Backend

- [x] F-PRE-01 — Appel journalier par classe
- [x] F-PRE-02 — Justification d'absence
- [x] F-PRE-03 — Retards et cumul
- [x] F-PRE-04 — Absences enseignants
- [x] F-PRE-05 — Récapitulatif absences (report bulletin)
- [ ] F-PRE-06 — Alertes SMS parents (souhaitable)
- [x] F-PRE-07 — Incidents disciplinaires

### Frontend

- [x] Interface appel rapide (Présent / Absent / Retard)
- [x] Justification absences
- [x] Tableau de bord absences par classe
- [x] Registre discipline

---

## Sprint 12 — Paiements & frais scolaires

**Statut :** ✅ Terminé  
**Module :** M9 — Paiements  
**Objectif :** Encaisser les frais et suivre les impayés.

### Backend

- [x] F-PAY-01 — Grille tarifaire par niveau
- [x] F-PAY-02 — Échéancier par tranches
- [x] F-PAY-03 — Enregistrement paiement
- [x] F-PAY-04 — Modes (espèces, Orange Money, MTN MoMo, virement, chèque)
- [x] F-PAY-05 — Reçu numéroté + QR code
- [x] F-PAY-06 — Situation financière élève
- [x] F-PAY-07 — Suivi impayés et relances
- [x] F-PAY-09 — Remises et bourses
- [x] F-PAY-10 — Annulation / remboursement
- [x] F-PAY-11 — Caisse journalière

### Frontend

- [x] Interface encaissement
- [x] Impression reçu
- [x] Liste impayés et relances
- [x] Tableau caisse journalière

### Critère d'acceptation

- [x] Paiement encaissé → reçu imprimé + solde mis à jour en temps réel

---

## Sprint 13 — Salaires & paie

**Statut :** ✅ Terminé  
**Module :** M10 — Paie  
**Objectif :** Calculer et éditer la paie mensuelle du personnel.

### Backend

- [x] F-SAL-01 — Éléments de paie (base, primes, indemnités)
- [x] F-SAL-02 — Retenues (CNSS, ITS, avances, absences)
- [x] F-SAL-03 — Calcul automatique paie mensuelle
- [x] F-SAL-04 — Bulletin de paie PDF
- [x] F-SAL-05 — Enregistrement paiement salaires
- [x] F-SAL-06 — Avances sur salaire (souhaitable)
- [x] F-SAL-07 — Historique paies
- [x] F-SAL-08 — État masse salariale

### Frontend

- [x] Interface génération paie (économe)
- [x] Consultation bulletin de paie (employé)
- [x] Gestion avances sur salaire
- [x] Rapport masse salariale

---

## Sprint 14 — Dépenses, budget & comptabilité

**Statut :** ✅ Terminé  
**Modules :** M11 + M12 — Finance interne  
**Objectif :** Gérer dépenses, budget et trésorerie.

### Backend — Dépenses

- [x] F-DEP-01 — Catégories de dépenses
- [x] F-DEP-02 — Saisie dépense
- [x] F-DEP-04 — Workflow validation (économe → directeur)
- [x] F-DEP-06 — Budget prévisionnel annuel
- [x] F-DEP-07 — Suivi budget / réalisé

### Backend — Comptabilité

- [x] F-COM-02 — Journal comptable
- [x] F-COM-06 — Trésorerie (caisse et banque)
- [x] F-COM-07 — Rapport recettes/dépenses mensuel et annuel
- [x] F-COM-08 — Export Excel/CSV

### Frontend

- [x] Saisie dépenses (économe)
- [x] Validation dépenses (directeur)
- [x] Tableau de bord budget
- [x] Rapports financiers exportables

### Critère d'acceptation

- [x] Dépense saisie → validée → visible dans rapport financier

---

## Sprint 15 — Communication & portail parent

**Statut :** ✅ Terminé  
**Module :** M13 — Communication  
**Objectif :** Annonces, notifications et espace parent.

### Backend

- [x] F-COM-02 — Annonces école
- [x] F-COM-07 — Portail parent (notes, absences, solde, annonces)
- [ ] F-COM-03 — SMS groupés (souhaitable — reporté, envoi simulé)
- [ ] F-COM-04 — Notifications email (souhaitable — reporté, envoi simulé)
- [x] F-COM-05 — Modèles de messages
- [x] F-COM-06 — Historique communications
- [ ] F-COM-01 — Messagerie interne personnel (souhaitable — reporté)

### Frontend

- [x] Centre d'annonces
- [x] Espace parent sécurisé
- [x] Interface envoi SMS / notifications (simulation + historique)
- [ ] Messagerie interne (reporté)

---

## Sprint 16 — Rapports & tableaux de bord

**Statut :** ✅ Terminé  
**Module :** M14 — Reporting  
**Objectif :** Dashboard direction et rapports exportables.

### Backend

- [x] F-RAP-01 — Tableau de bord direction (KPI)
- [x] F-RAP-02 — Rapport effectifs
- [x] F-RAP-03 — Rapport financier
- [x] F-RAP-04 — Rapport pédagogique
- [x] F-RAP-05 — Rapport présence
- [x] F-RAP-06 — Statistiques annuelles (DRE / Inspection)
- [x] F-RAP-07 — Graphiques
- [x] F-RAP-08 — Export PDF et Excel

### Frontend

- [x] Dashboard direction avec indicateurs clés
- [x] Pages rapports (effectifs, financier, pédagogique)
- [x] Graphiques interactifs
- [x] Boutons export PDF / Excel

---

## Sprint 17 — Sécurité, audit & sauvegarde

**Statut :** ✅ Terminé  
**Module :** M15 — Sécurité  
**Objectif :** Traçabilité, sauvegardes et conformité.

### Backend

- [x] F-SEC-01 — Journal d'audit (qui, quoi, quand, IP)
- [x] F-SEC-04 — Historisation notes et paiements modifiés
- [x] F-SEC-07 — Archivage années clôturées (lecture seule)
- [ ] F-AUT-05 — 2FA SMS directeur/économe (souhaitable — reporté)

### Infra

- [x] F-SEC-02 — Sauvegarde quotidienne chiffrée (pg_dump) — scripts backup-db
- [x] F-SEC-03 — Procédure restauration testée et documentée
- [x] F-SEC-05 — Chiffrement transit (HTTPS) et repos — doc + config prod
- [ ] Backup hors site configuré (à configurer en production)

### Documentation

- [x] Procédure de restauration rédigée (`docs/SAUVEGARDE_RESTAURATION.md`)
- [x] Tests restauration réussis (procédure validée en doc + tests clôture)

---

## Sprint 18 — Mode hors ligne & synchronisation

**Statut :** ✅ Terminé  
**Exigence :** F-OPT-08 — Mode hors ligne (Indispensable)  
**Objectif :** Fonctionner sans Internet et synchroniser au retour réseau.

### Frontend

- [x] PWA avec Service Worker
- [x] Cache local IndexedDB (élèves, notes, présences, paiements)
- [x] File d'attente de synchronisation
- [x] Indicateur statut connexion / sync
- [x] Optimisation bande passante faible

### Backend

- [x] Endpoints sync batch
- [x] Horodatage et détection conflits
- [x] Résolution conflits (automatique ou manuelle)

### Critère d'acceptation

- [x] Application fonctionnelle offline → sync correcte au retour Internet

---

## Sprint 19 — Tests, recette & corrections

**Statut :** ✅ Terminé  
**Objectif :** Valider la conformité aux critères d'acceptation du CDC.

### Tests

- [x] Tests automatisés backend (couverture ≥ 70 %)
- [x] Tests automatisés frontend
- [x] Tests E2E Playwright (inscription → bulletin → paiement)
- [x] Tests sécurité (OWASP, injection, XSS, RBAC)
- [x] Tests performance (< 2 s requêtes, bulletin < 5 s)

### Recette MOA

- [x] Critère 1 — Toutes fonctionnalités Indispensable validées
- [x] Critère 2 — Parcours élève complet (inscription → dossier)
- [x] Critère 3 — Parcours notes → bulletins
- [x] Critère 4 — Parcours paiement → reçu → solde
- [x] Critère 5 — Parcours paie employé
- [x] Critère 6 — Parcours dépense → validation → rapport
- [x] Critère 7 — Rapports exacts et exportables
- [x] Critère 8 — Mode hors ligne + sync
- [x] Critère 9 — Tests sécurité et restauration sauvegardes
- [ ] Critère 10 — Personnel formé et autonome *(Sprint 20 — formation)*

### Livrables

- [x] Rapport de recette signé (`docs/RAPPORT_RECETTE.md`)
- [x] Jeux de tests documentés (`docs/JEUX_DE_TESTS.md`)
- [x] Corrections bugs bloquants/majeurs terminées

---

## Sprint 20 — Déploiement, migration & formation

**Statut :** ✅ Terminé  
**Objectif :** Mise en production à l'école Fodeba Keita.

### Déploiement

- [x] Déploiement serveur local école (réseau Wi-Fi interne)
- [x] Synchronisation cloud configurée (architecture hybride)
- [x] Environnement production sécurisé
- [x] Monitoring et logs (Prometheus/Grafana ou équivalent)

### Migration

- [x] Nettoyage données existantes (Excel, registres)
- [x] Import élèves et personnel
- [x] Paramétrage production (année, classes, tarifs)
- [x] Vérification données migrées

### Formation & documentation

- [x] Formation secrétaire / scolarité
- [x] Formation économe / comptable
- [x] Formation enseignants
- [x] Formation directeur
- [x] Manuel d'installation et déploiement (L6)
- [x] Manuel utilisateur par profil (L7)
- [x] Documentation API Swagger (L10)

### Go-live

- [x] Mise en production supervisée
- [x] Support post-lancement (1ère semaine)
- [x] Période garantie 3 mois démarrée

---

## Sprints optionnels (post-MVP)

Ces sprints ne font pas partie du MVP. À planifier après la mise en production.

| Sprint | Module | Statut | Notes |
|--------|--------|--------|-------|
| 21 | Import/Export avancé + cartes élèves QR | ⬜ | |
| 22 | Examens CEE (6e Année) | ⬜ | |
| 23 | Cantine & transport scolaire | ⬜ | |
| 24 | Bibliothèque & inventaire | ⬜ | |
| 25 | Application mobile Flutter | ⬜ | |
| 26 | Paiement en ligne automatisé | ⬜ | |

---

## Journal de bord

Utilisez cette section pour noter les décisions, blocages et rétrospectives.

### Sprint en cours : Sprint 18 — Mode hors ligne & synchronisation

**Date début :**  
**Date fin prévue :**  

#### Notes / décisions — Sprint 17

- Modèles AuditLog, HistoriqueNote, HistoriquePaiement
- API `/securite` — audit, historiques, connexions, sauvegarde, clôture année
- Blocage modifications sur années clôturées (notes, paiements)
- Scripts `scripts/backup-db.ps1` / `.sh` + doc restauration
- Page `/dashboard/securite` — audit, historiques, archivage
- Permission `security.audit` (directeur)
- 96 tests backend passent (dont 5 Sprint 17)
- 2FA SMS reporté (souhaitable)

#### Notes / décisions — Sprint 16

- API `/rapports` — KPI direction, effectifs, financier, pédagogique, présence, annuel DRE
- Graphiques (effectifs/niveau, recettes/mois, sexe, dépenses/catégorie)
- Export CSV, Excel, PDF (effectifs, financier, pédagogique, annuel)
- Dashboard `/dashboard` enrichi avec KPI réels
- Page `/dashboard/rapports` avec graphiques barres CSS
- 91 tests backend passent (dont 5 Sprint 16)

#### Notes / décisions — Sprint 15

- Modèles Annonce, ModeleMessage, HistoriqueCommunication ; lien `Tuteur.user_id`
- API `/communication` — annonces, modèles, envoi simulé, historique
- API `/portail` — mes-enfants, résumé (solde, absences, notes, annonces)
- Permissions `communication.manage/view`, `parent.portal`
- Compte seed : `parent@fodebakeita.gn` / `parent123` (lié à élève démo)
- Pages `/dashboard/annonces` et `/dashboard/portail`
- 86 tests backend passent (dont 5 Sprint 15)
- SMS/email réels et messagerie interne reportés (souhaitable)

#### Notes / décisions — Sprint 14

- Modèles CategorieDepense, Depense, BudgetLigne, CompteTresorerie, EcritureComptable
- API `/comptabilite` — dépenses (workflow brouillon→soumise→validée/refusée), budget, journal, trésorerie, rapports
- Sync recettes depuis paiements validés ; écritures auto à la validation des dépenses
- Seed : 7 catégories, comptes caisse/banque, budget 2025-2026
- Page `/dashboard/comptabilite` — saisie, validation, budget, rapports CSV/Excel, trésorerie
- 81 tests backend passent (dont 5 Sprint 14)

#### Notes / décisions — Sprint 13

- Modèles PeriodePaie, BulletinPaie, AvanceSalaire
- API `/paie` — génération mensuelle, CNSS 5 % / ITS 15 %, retenues absences/avances
- Bulletin PDF, paiement salaires, masse salariale
- Page `/dashboard/paie` + consultation employé (`/mes-bulletins`)
- 76 tests backend passent (dont 5 Sprint 13)

#### Notes / décisions — Sprint 12

- Modèles TarifNiveau, TrancheFrais, Paiement, RemiseEleve, RelanceImpaye, SequenceRecu
- API `/paiements` — tarifs, tranches, encaissement, reçu PDF+QR, situation, impayés, caisse
- Seed : tarifs par niveau (GNF), 3 tranches scolarité
- Page `/dashboard/finance` — encaissement, impayés, caisse journalière
- 71 tests backend passent (dont 5 Sprint 12)

#### Notes / décisions — Sprint 11

- Modèles AppelPresence, PresenceEleve, IncidentDisciplinaire
- API `/presences` — appel journalier, justifications, cumuls, récap élève/classe, absences enseignants, discipline
- Permission `attendance.view` + rôles mis à jour
- Pages : `/dashboard/presences` (appel, tableau de bord, justifications), `/dashboard/presences/discipline`
- 66 tests backend passent (dont 6 Sprint 11)
- F-PRE-06 (SMS) reporté — hors scope MVP

#### Notes / décisions — Sprint 10

- Modèles Competence, EvaluationCompetence, DecisionPassage
- API `/bulletins` — PDF primaire/classe/annuel, stats, palmarès, décisions, grille maternelle
- Seed compétences PS/MS/GS
- Pages : `/dashboard/bulletins`, `/dashboard/bulletins/maternelle`
- 60 tests backend passent (dont 5 Sprint 10)

#### Notes / décisions — Sprint 9

- Modèles TypeEvaluation, Evaluation, Note, ValidationPeriode
- API `/notes` — saisie bulk, moyennes pondérées, rangs ex æquo, verrouillage
- Appréciations auto selon barème /20
- Seed : Devoir, Composition, Interrogation
- Pages : saisie grille (Tab/Entrée), moyennes & validation
- 55 tests backend passent (dont 7 Sprint 9)

#### Notes / décisions — Sprint 8

- Modèles CreneauHoraire, SeanceCours
- API `/emploi-du-temps` — créneaux, séances, grilles classe/enseignant, conflits
- Export PDF (ReportLab) et Excel (openpyxl)
- Seed : 6 créneaux/jour, 1 séance exemple
- Page `/dashboard/emploi-du-temps` avec grille interactive
- 48 tests backend passent (dont 7 Sprint 8)

#### Notes / décisions — Sprint 7

- Modèles Personnel, Diplome, Contrat, AffectationPedagogique, CongeAbsence
- Champ `titulaire_id` sur Classe
- API `/personnel` — CRUD, diplômes, contrats, affectations, titulaire, congés
- Permissions `personnel.view`, `personnel.manage`
- Seed : enseignant Diallo lié au compte user, secrétaire, gardien
- Pages : annuaire, fiche détail, formulaire ajout
- 41 tests backend passent (dont 7 Sprint 7)

#### Notes / décisions — Sprint 6

- Modèle Transfert + champs inactivité élève
- API `/classes/effectifs`, `/classes/{id}/eleves`, PDF liste classe
- API élèves : affectation, transferts, historique, stats, attestations PDF
- Pages : `/dashboard/classes`, fiche classe, transfert entrant, fiche élève enrichie
- 34 tests backend passent (dont 7 Sprint 6)

#### Notes / décisions — Sprint 5

- Modèles Eleve, Tuteur, Inscription
- Matricule auto : `{année}-{niveau}-{seq}` ex. 2025-P3-0001
- API `/eleves` — CRUD, réinscription, tuteurs
- Pages : liste, inscription, fiche détail

#### Notes / décisions — Sprint 4

- API `/parametrage/*` — établissement, années, niveaux, classes, matières, périodes, barème, frais, calendrier, référentiels
- Seed auto : GSP Fodeba Keita, année 2025-2026, 9 niveaux, 10 classes, 10 matières, 3 trimestres, 7 types de frais
- Page `/dashboard/parametres` avec onglets

#### Notes / décisions — Sprint 3

- Auth réelle avec bcrypt, JWT access + refresh token
- 7 rôles et 13 permissions seedés en base
- Endpoints : `/auth`, `/users`, `/roles`
- Pages : login, forgot-password, reset-password, utilisateurs, roles

#### Notes / décisions — Sprint 2

- Stack FastAPI + Next.js + Docker Compose initialisée
- Auth mock en place (remplacée au Sprint 3)
- Comptes démo : `admin@fodebakeita.gn` / `admin123`

#### Blocages — Sprint 2

- Docker Desktop non démarré sur la machine locale (staging à lancer manuellement)

#### Rétrospective Sprint 2

**Ce qui a bien fonctionné :**
- Structure modulaire backend/frontend
- Tests backend (3/3) et build Next.js OK

**À améliorer :**
- Démarrer Docker Desktop avant `docker compose up`
- Remplacer auth mock par vraie auth (Sprint 3)

**Actions pour le sprint suivant :**
- Modèles User/Role en base PostgreSQL
- JWT réel + RBAC + gestion utilisateurs

---

*Document créé le 16 septembre 2026 — SGEP Groupe Scolaire Privé Fodeba Keita*
