# L10 — Documentation API (Swagger / OpenAPI)

## Accès

| Environnement | URL |
|---------------|-----|
| Développement | http://localhost:8000/docs |
| Production | http://[IP-SERVEUR]/docs |

Documentation alternative (ReDoc) : `/redoc`  
Schéma OpenAPI JSON : `/api/v1/openapi.json`

---

## Authentification

1. **POST** `/api/v1/auth/login`
   ```json
   { "email": "admin@fodebakeita.gn", "password": "admin123" }
   ```
2. Copier le `access_token` de la réponse
3. Dans Swagger : bouton **Authorize** → `Bearer <token>`

---

## Modules API

| Préfixe | Description |
|---------|-------------|
| `/api/v1/auth` | Connexion, refresh, profil |
| `/api/v1/users` | Gestion utilisateurs |
| `/api/v1/eleves` | Élèves et inscriptions |
| `/api/v1/notes` | Évaluations et notes |
| `/api/v1/bulletins` | Bulletins PDF |
| `/api/v1/paiements` | Encaissements |
| `/api/v1/presences` | Appels et discipline |
| `/api/v1/sync` | Synchronisation offline |
| `/api/v1/rapports` | Rapports et KPI |
| `/api/v1/securite` | Audit et clôture |

---

## Santé et métriques

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | État API, DB, Redis |
| `GET /metrics` | Métriques Prometheus |

---

## Codes de réponse

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 201 | Créé |
| 401 | Non authentifié |
| 403 | Permission insuffisante |
| 404 | Ressource introuvable |
| 422 | Données invalides |

---

## Production

En production, limiter l'accès à `/docs` au réseau administrateur ou le protéger via nginx (authentification basique).
