# Rapport de recette — SGEP Fodeba Keita

**Projet :** Système de Gestion d'École Primaire  
**Établissement :** Groupe Scolaire Privé Fodeba Keita — Conakry  
**Version :** MVP (Sprints 0–19)  
**Date :** _______________

---

## 1. Synthèse

| Indicateur | Résultat |
|------------|----------|
| Tests backend automatisés | ___ / ___ passés |
| Couverture backend | ___ % |
| Tests frontend (Vitest) | ___ / ___ passés |
| Tests E2E Playwright | ___ / ___ passés |
| Bugs bloquants ouverts | ___ |
| Bugs majeurs ouverts | ___ |

**Décision recette :** ☐ Acceptée  ☐ Acceptée avec réserves  ☐ Refusée

---

## 2. Critères MOA (CDC)

| # | Critère | Statut | Preuve / test |
|---|---------|--------|---------------|
| 1 | Fonctionnalités Indispensable validées | ☐ | Suite pytest complète |
| 2 | Parcours élève (inscription → dossier) | ☐ | `test_parcours_api`, E2E |
| 3 | Parcours notes → bulletins | ☐ | `test_notes`, `test_bulletins` |
| 4 | Parcours paiement → reçu → solde | ☐ | `test_paiements`, `test_parcours_api` |
| 5 | Parcours paie employé | ☐ | `test_paie` |
| 6 | Parcours dépense → validation → rapport | ☐ | `test_comptabilite` |
| 7 | Rapports exacts et exportables | ☐ | `test_rapports` |
| 8 | Mode hors ligne + sync | ☐ | `test_sync` |
| 9 | Sécurité et sauvegarde | ☐ | `test_security_owasp`, `test_securite`, `docs/SAUVEGARDE_RESTAURATION.md` |
| 10 | Personnel formé et autonome | ☐ | Sprint 20 — formation |

---

## 3. Tests sécurité

| Test | Résultat |
|------|----------|
| Authentification obligatoire | ☐ |
| RBAC par rôle | ☐ |
| Injection SQL (recherche) | ☐ |
| XSS stocké (nom élève) | ☐ |
| Verrouillage après échecs login | ☐ |
| Année clôturée en lecture seule | ☐ |

---

## 4. Tests performance

| Endpoint | Seuil | Mesuré | OK |
|----------|-------|--------|-----|
| Liste élèves | < 2 s | | ☐ |
| KPI dashboard | < 2 s | | ☐ |
| Sync pull | < 2 s | | ☐ |
| Bulletin PDF | < 5 s | | ☐ |

---

## 5. Anomalies et réserves

| ID | Sévérité | Description | Statut |
|----|----------|-------------|--------|
| | | | |

---

## 6. Signatures

| Rôle | Nom | Signature | Date |
|------|-----|-----------|------|
| MOA / Direction | | | |
| Prestataire / Équipe technique | | | |
