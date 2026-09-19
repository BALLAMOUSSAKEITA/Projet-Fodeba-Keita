# Sauvegarde et restauration — SGEP Fodeba Keita

## Sauvegarde quotidienne

### Windows (PowerShell)

```powershell
$env:POSTGRES_PASSWORD = "votre_mot_de_passe"
.\scripts\backup-db.ps1
```

### Linux / Docker

```bash
export POSTGRES_PASSWORD=sgep_dev_password
./scripts/backup-db.sh
```

Les fichiers sont stockés dans `backend/backups/`.

### Planification

- **Production** : planifier via Task Scheduler (Windows) ou cron (Linux) à 2h00.
- **Hors site** : copier `backend/backups/` vers un stockage externe chiffré (cloud, NAS).

## Restauration

1. Arrêter l'API SGEP.
2. Restaurer la base :

```bash
# Depuis un dump .sql.gz
gunzip -c backend/backups/sgep_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U sgep -d sgep_db
```

3. Relancer les services : `docker compose up -d`
4. Vérifier : `GET /api/v1/health`

## Chiffrement

- **Transit** : HTTPS obligatoire en production (reverse proxy nginx/Traefik).
- **Repos** : chiffrer les dumps avec GPG avant copie hors site :

```bash
gpg --symmetric --cipher-algo AES256 backup.sql.gz
```

## Tests de restauration

Effectuer un test trimestriel sur un environnement staging :

1. Créer une sauvegarde.
2. Restaurer sur une base `sgep_db_restore`.
3. Lancer `pytest` et vérifier la connexion admin.
