# Checklist Go-Live — Fodeba Keita

## J-7 — Préparation

- [ ] Serveur installé et Docker opérationnel
- [ ] `.env.production` configuré (mots de passe uniques)
- [ ] `deploy-local.sh` exécuté avec succès
- [ ] Monitoring Prometheus/Grafana actif (optionnel)
- [ ] Sauvegarde automatique planifiée (cron / Task Scheduler)
- [ ] Sync cloud testée si activée
- [ ] Données migrées (`import_migration.py verify`)
- [ ] Comptes utilisateurs réels créés (directeur, secrétaire, économe, enseignants)

## J-1 — Recette finale

- [ ] Parcours inscription → bulletin → paiement validé
- [ ] Mode hors ligne testé sur 1 poste enseignant
- [ ] Rapport de recette signé (`docs/RAPPORT_RECETTE.md`)
- [ ] Formations réalisées (voir `docs/FORMATION.md`)
- [ ] Manuels distribués aux équipes

## Jour J — Mise en production

- [ ] Bascule DNS / IP définitive (`PUBLIC_URL`)
- [ ] Anciens registres Excel archivés (lecture seule)
- [ ] Équipe informée : **ne plus saisir dans Excel**
- [ ] Support technique disponible sur site
- [ ] Point de situation fin de journée

## Semaine 1 — Support post-lancement

| Jour | Action |
|------|--------|
| J+1 | Vérifier sauvegardes, corriger bugs urgents |
| J+2 | Accompagnement secrétariat (inscriptions) |
| J+3 | Accompagnement enseignants (notes/présences) |
| J+4 | Accompagnement économe (paiements) |
| J+5 | Bilan semaine avec directeur |

## Garantie 3 mois

- [ ] Date de début garantie : _______________
- [ ] Date de fin garantie : _______________
- [ ] Contact support : _______________

**Signatures go-live**

| Rôle | Nom | Date |
|------|-----|------|
| Directeur | | |
| Responsable technique | | |
