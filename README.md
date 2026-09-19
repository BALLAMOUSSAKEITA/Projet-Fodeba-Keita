# SGEP — Groupe Scolaire Privé Fodeba Keita

Plateforme de gestion scolaire (maternelle & primaire) — Conakry, Guinée.

## Stack

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI + SQLAlchemy + Alembic |
| Frontend | Next.js 16 + TypeScript + TailwindCSS |
| Base de données | PostgreSQL 15 |
| Cache | Redis 7 |
| Fichiers | MinIO (compatible S3) |

## Démarrage rapide

### Prérequis

- Docker & Docker Compose
- Node.js 20+ (développement frontend local)
- Python 3.12+ (développement backend local)

### 1. Configuration

```bash
cp .env.example .env
```

### 2. Lancer l'infrastructure (PostgreSQL, Redis, MinIO, API)

```bash
docker compose up -d
```

- API : http://localhost:8000
- Swagger : http://localhost:8000/docs
- MinIO Console : http://localhost:9001

### 3. Frontend (développement local)

```bash
cd frontend
npm install
npm run dev
```

- Application : http://localhost:3000

### Comptes par défaut (seed)

| Email | Mot de passe | Rôle |
|-------|--------------|------|
| admin@fodebakeita.gn | admin123 | Super admin |
| directeur@fodebakeita.gn | directeur123 | Directeur |
| enseignant@fodebakeita.gn | enseignant123 | Enseignant |

### API Auth (Sprint 3)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/auth/login` | Connexion |
| POST | `/api/v1/auth/refresh` | Renouveler le token |
| GET | `/api/v1/auth/me` | Profil connecté |
| POST | `/api/v1/auth/forgot-password` | Demande reset |
| POST | `/api/v1/auth/reset-password` | Réinitialiser |
| GET/POST | `/api/v1/users` | Gestion utilisateurs |
| GET | `/api/v1/roles` | Rôles et permissions |

## Structure du projet

```
├── backend/          # API FastAPI
├── frontend/         # Application Next.js
├── docker-compose.yml
├── SPRINTS.md        # Suivi des sprints
└── README.md
```

## Commandes utiles

```bash
# Backend — tests
cd backend && pytest -v

# Backend — migrations Alembic
cd backend && alembic revision --autogenerate -m "description"
cd backend && alembic upgrade head

# Docker — logs API
docker compose logs -f api
```

## Déploiement production (école)

```bash
cp .env.production.example .env.production
# Éditer PUBLIC_URL et mots de passe
./scripts/deploy-local.sh   # ou .\scripts\deploy-local.ps1
```

Monitoring : `docker compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d`

## Déploiement Railway (cloud)

Guide complet : [`docs/DEPLOIEMENT_RAILWAY.md`](docs/DEPLOIEMENT_RAILWAY.md)

1. Créer un projet Railway lié au dépôt GitHub
2. Ajouter **PostgreSQL**
3. Service **backend** (root: `backend`) + variables `SECRET_KEY`, `CORS_ORIGINS`
4. Service **frontend** (root: `frontend`) + `NEXT_PUBLIC_API_URL` = URL du backend

## Documentation

| Document | Description |
|----------|-------------|
| `SPRINTS.md` | Suivi des sprints |
| `docs/MANUEL_INSTALLATION.md` | L6 — Installation & déploiement |
| `docs/MANUEL_UTILISATEUR.md` | L7 — Guide par profil |
| `docs/API_SWAGGER.md` | L10 — Documentation API |
| `docs/MIGRATION_DONNEES.md` | Import CSV Excel → SGEP |
| `docs/FORMATION.md` | Plans de formation |
| `docs/GOLIVE_CHECKLIST.md` | Checklist mise en production |
| `docs/JEUX_DE_TESTS.md` | Catalogue des tests |
| `docs/SAUVEGARDE_RESTAURATION.md` | Backup & restore |
