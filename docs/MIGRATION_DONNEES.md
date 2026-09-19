# Migration des données — Excel vers SGEP

## 1. Préparation (nettoyage Excel)

1. Exporter chaque registre Excel en **CSV UTF-8**
2. Supprimer les lignes vides et doublons (même nom + prénoms + date naissance)
3. Uniformiser les dates : `AAAA-MM-JJ` ou `JJ/MM/AAAA`
4. Vérifier les codes niveaux : `PS`, `MS`, `GS`, `1A`…`6A`
5. Vérifier les noms de classes exacts (ex. `3e Année A`)

Modèles CSV : `data/migration/templates/`

---

## 2. Ordre d'import

1. **Paramétrage** — vérifier année active, classes, tarifs via l'interface admin
2. **Personnel** — `personnel.csv`
3. **Élèves** — `eleves.csv`
4. **Vérification** — commande `verify`

---

## 3. Commandes d'import

```bash
# Depuis le conteneur API
docker exec -it sgep-api python scripts/import_migration.py personnel /data/migration/personnel.csv
docker exec -it sgep-api python scripts/import_migration.py eleves /data/migration/eleves.csv
docker exec -it sgep-api python scripts/import_migration.py verify
```

**Développement local :**

```bash
cd backend
python scripts/import_migration.py eleves ../data/migration/eleves.csv
python scripts/import_migration.py verify
```

---

## 4. Colonnes CSV élèves

| Colonne | Obligatoire | Exemple |
|---------|-------------|---------|
| nom | Oui | Keita |
| prenoms | Oui | Aminata |
| sexe | Oui | F ou M |
| date_naissance | Oui | 2018-03-15 |
| niveau_code | Oui | GS |
| classe_nom | Non | Grande Section A |
| tuteur_type | Non | pere / mere / tuteur |
| tuteur_nom | Oui | Keita |
| tuteur_prenoms | Oui | Amadou |
| tuteur_telephone | Oui | +224621000001 |

---

## 5. Colonnes CSV personnel

| Colonne | Obligatoire | Exemple |
|---------|-------------|---------|
| nom | Oui | Camara |
| prenoms | Oui | Fatoumata |
| sexe | Non | F |
| telephone | Oui | +224622000001 |
| categorie | Oui | enseignant / non_enseignant |
| fonction | Non | Enseignant |
| specialite | Non | Français |
| date_embauche | Non | 2020-09-01 |

---

## 6. Vérification post-migration

- [ ] Effectifs par classe cohérents avec les registres papier
- [ ] Échantillon de 10 fiches élèves vérifiées manuellement
- [ ] Annuaire personnel complet
- [ ] Tarifs et tranches conformes au board de direction
- [ ] Comptes utilisateurs créés pour chaque profil
