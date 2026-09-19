# L6 — Manuel d'installation et déploiement

**SGEP — Groupe Scolaire Privé Fodeba Keita**  
**Version :** MVP 1.0

---

## 1. Prérequis matériel (serveur école)

| Composant | Minimum recommandé |
|-----------|-------------------|
| Processeur | 4 cœurs |
| RAM | 8 Go |
| Disque | 100 Go SSD |
| Réseau | Wi-Fi interne + Ethernet |
| OS | Ubuntu 22.04 LTS ou Windows Server 2019+ |

Logiciels : **Docker 24+**, **Docker Compose v2**.

---

## 2. Installation rapide (production)

```bash
# 1. Cloner / copier le projet sur le serveur
cd /opt/sgep

# 2. Configurer l'environnement production
cp .env.production.example .env.production
# Éditer : PUBLIC_URL, mots de passe, SECRET_KEY

# 3. Déployer
chmod +x scripts/deploy-local.sh
./scripts/deploy-local.sh
```

**Windows (PowerShell) :**

```powershell
.\scripts\deploy-local.ps1
```

L'application est accessible à l'adresse configurée dans `PUBLIC_URL` (ex. `http://192.168.1.10`).

---

## 3. Architecture déployée

```
[Postes Wi-Fi école] → [Nginx :80] → Frontend Next.js
                                    → API FastAPI (/api/)
                                    → Swagger (/docs)
         ↓
    PostgreSQL + Redis + MinIO (réseau interne Docker)
```

### Monitoring (optionnel)

```bash
docker compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d
```

| Service | URL | Défaut |
|---------|-----|--------|
| Prometheus | `:9090` | Métriques API |
| Grafana | `:3001` | Dashboards (admin / voir .env) |

---

## 4. Sécurisation production

1. **Changer tous les mots de passe** dans `.env.production`
2. **SECRET_KEY** : générer une clé aléatoire de 64 caractères minimum
3. **Pare-feu** : n'exposer que le port 80 (HTTP) sur le réseau local
4. **HTTPS** : ajouter un certificat (Let's Encrypt ou certificat interne) via nginx si accès externe
5. **Sauvegardes** : planifier `scripts/backup-db.ps1` ou `.sh` (quotidien)
6. **Sync cloud** : activer `CLOUD_SYNC_*` pour copie distante des sauvegardes

---

## 5. Architecture hybride (local + cloud)

| Composant | Local (école) | Cloud (optionnel) |
|-----------|---------------|-------------------|
| Application | Serveur Docker | — |
| Base de données | PostgreSQL local | Sauvegarde rsync/scp |
| Fichiers | MinIO local | Sync sauvegarde |
| Mode offline | PWA + sync batch | Pull/push au retour réseau |

Script sync : `scripts/sync-cloud.sh` ou `sync-cloud.ps1`

---

## 6. Migrations Alembic

```bash
docker exec -it sgep-api alembic upgrade head
```

---

## 7. Import des données existantes

Voir `docs/MIGRATION_DONNEES.md`.

---

## 8. Dépannage

| Problème | Solution |
|----------|----------|
| Page blanche | `docker compose -f docker-compose.prod.yml logs frontend` |
| Erreur 502 | Vérifier `docker compose logs api` |
| Connexion refusée | Vérifier `PUBLIC_URL` et `CORS_ORIGINS` |
| Base vide | Attendre le seed au premier démarrage API (~30 s) |

---

## 9. Support post-lancement

- **Semaine 1** : support sur site ou à distance (voir `docs/GOLIVE_CHECKLIST.md`)
- **Garantie** : 3 mois après go-live
