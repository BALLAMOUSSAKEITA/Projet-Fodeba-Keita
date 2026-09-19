# Déploiement SGEP sur Railway

Guide pas à pas pour héberger **backend**, **frontend** et **PostgreSQL** sur [Railway](https://railway.app).

---

## Architecture Railway

```
[Utilisateur] → Frontend (Next.js) → Backend (FastAPI) → PostgreSQL
                                      ↘ Redis (optionnel)
```

| Service Railway | Dossier racine | Port |
|-----------------|----------------|------|
| `sgep-api` | `/backend` | `$PORT` (auto) |
| `sgep-web` | `/frontend` | `$PORT` (auto) |
| PostgreSQL | Plugin Railway | — |
| Redis | Plugin (optionnel) | — |

---

## 1. Prérequis

- Compte [Railway](https://railway.app) (GitHub connecté)
- Dépôt GitHub : `BALLAMOUSSAKEITA/Projet-Fodeba-Keita`

---

## 2. Créer le projet

1. [Railway Dashboard](https://railway.app/dashboard) → **New Project**
2. **Deploy from GitHub repo** → sélectionner `Projet-Fodeba-Keita`

---

## 3. PostgreSQL

1. Dans le projet → **+ New** → **Database** → **PostgreSQL**
2. Railway crée automatiquement `DATABASE_URL`

---

## 4. Service Backend (`sgep-api`)

1. **+ New** → **GitHub Repo** → même dépôt (ou dupliquer le service existant)
2. **Settings** :
   - **Service name** : `sgep-api`
   - **Root Directory** : `backend`
   - **Builder** : Dockerfile (détecté via `backend/railway.toml`)

3. **Variables** (onglet Variables) :

| Variable | Valeur |
|----------|--------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (référence au plugin) |
| `SECRET_KEY` | Clé aléatoire longue (64+ caractères) |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | URL du frontend (étape 5) — ex. `https://sgep-web-production.up.railway.app` |

4. **Networking** → **Generate Domain** → noter l'URL publique, ex. :
   `https://sgep-api-production-xxxx.up.railway.app`

5. Au déploiement, `start.sh` exécute automatiquement :
   - `alembic upgrade head`
   - seed initial (via `lifespan` FastAPI)
   - démarrage uvicorn sur `$PORT`

6. Vérifier : `https://VOTRE-API.up.railway.app/api/v1/health`

---

## 5. Service Frontend (`sgep-web`)

1. **+ New** → **GitHub Repo** → même dépôt
2. **Settings** :
   - **Service name** : `sgep-web`
   - **Root Directory** : `frontend`

3. **Variables** :

| Variable | Valeur |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | URL publique du backend (sans slash final) |
| | ex. `https://sgep-api-production-xxxx.up.railway.app` |

> **Important** : `NEXT_PUBLIC_API_URL` est lue au **build**. Après modification, redéployer le frontend (**Redeploy**).

4. **Networking** → **Generate Domain**

5. Retourner sur le **backend** → mettre à jour `CORS_ORIGINS` avec l'URL du frontend → **Redeploy** backend.

6. Ouvrir l'URL frontend → connexion :
   - `admin@fodebakeita.gn` / `admin123`

---

## 6. Redis (optionnel)

Sans Redis, l'API fonctionne (health = `degraded` pour Redis).

1. **+ New** → **Database** → **Redis**
2. Sur le backend, ajouter :
   ```
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

---

## 7. CLI Railway (optionnel)

```bash
npm install -g @railway/cli
railway login
railway link          # dans le dossier backend ou frontend
railway up
railway logs
```

---

## 8. Dépannage

| Problème | Solution |
|----------|----------|
| Erreur CORS | Vérifier `CORS_ORIGINS` = URL exacte du frontend (https) |
| Frontend ne joint pas l'API | Vérifier `NEXT_PUBLIC_API_URL` + redéployer frontend |
| Erreur DB / asyncpg | `DATABASE_URL` doit être liée au plugin Postgres (conversion auto) |
| Build frontend échoue | Vérifier les logs ; `npm run build` doit passer en local |
| 502 au démarrage | Attendre migrations (~30 s) ; consulter `railway logs` |

---

## 9. Coûts

Railway propose un crédit gratuit mensuel. Surveiller l'usage dans **Project Settings → Usage**.

---

## 10. Production école vs Railway

| | Railway (cloud) | Serveur local (docker-compose.prod) |
|--|-----------------|-------------------------------------|
| Accès | Internet | Wi-Fi interne école |
| Offline PWA | Sync au retour réseau | Mode offline complet |
| Recommandé pour | Démo, accès distant | Production quotidienne Fodeba Keita |

Les deux peuvent coexister (architecture hybride) via sync cloud documentée dans `docs/MANUEL_INSTALLATION.md`.
