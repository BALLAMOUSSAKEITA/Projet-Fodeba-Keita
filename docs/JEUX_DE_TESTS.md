# Jeux de tests — SGEP Fodeba Keita

Document de référence pour la recette et la maintenance (Sprint 19).

## Backend (pytest)

| Fichier | Couverture | Commande |
|---------|------------|----------|
| `test_auth.py` | Authentification, verrouillage, RBAC | `pytest tests/test_auth.py` |
| `test_eleves*.py` | Inscriptions, affectations, transferts | `pytest tests/test_eleves*.py` |
| `test_notes.py` | Évaluations, saisie, moyennes | `pytest tests/test_notes.py` |
| `test_bulletins.py` | PDF, palmarès, compétences | `pytest tests/test_bulletins.py` |
| `test_paiements.py` | Encaissement, impayés, reçus | `pytest tests/test_paiements.py` |
| `test_parcours_api.py` | **Parcours complet** inscription → bulletin → paiement | `pytest tests/test_parcours_api.py` |
| `test_security_owasp.py` | Injection SQL, XSS, RBAC, tokens | `pytest tests/test_security_owasp.py` |
| `test_performance.py` | Latence API < 2 s, bulletin < 5 s | `pytest tests/test_performance.py` |
| `test_sync.py` | Mode hors ligne / synchronisation | `pytest tests/test_sync.py` |
| `test_securite.py` | Audit, clôture année, historiques | `pytest tests/test_securite.py` |

**Suite complète :**

```bash
cd backend
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=70
```

## Frontend (Vitest)

| Fichier | Couverture |
|---------|------------|
| `src/lib/auth/session.test.ts` | Session, permissions |
| `src/lib/offline/sync-queue.test.ts` | File d'attente offline |

```bash
cd frontend
npm run test
```

## E2E (Playwright)

| Spec | Parcours |
|------|----------|
| `e2e/tests/parcours-complet.spec.ts` | Connexion UI + navigation + parcours API |

**Prérequis :** API sur `:8000`, frontend sur `:3000` (docker-compose ou dev local).

```bash
cd e2e
npm install
npx playwright install chromium
npm test
```

## Comptes de test (seed)

| Rôle | E-mail | Mot de passe |
|------|--------|--------------|
| Super admin | `admin@fodebakeita.gn` | `admin123` |
| Directeur | `directeur@fodebakeita.gn` | `directeur123` |
| Enseignant | `enseignant@fodebakeita.gn` | `enseignant123` |
| Parent | `parent@fodebakeita.gn` | `parent123` |

## Critères de performance

- Requêtes API courantes : **< 2 secondes**
- Génération bulletin PDF : **< 5 secondes**
- Couverture backend : **≥ 70 %**
