#!/usr/bin/env bash
# Déploiement production — serveur local école Fodeba Keita
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env.production ]]; then
  cp .env.production.example .env.production
  echo "Fichier .env.production créé — MODIFIEZ les mots de passe avant la mise en production."
fi

echo "=== Déploiement SGEP (production) ==="
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

PUBLIC_URL=$(grep -E '^PUBLIC_URL=' .env.production | cut -d= -f2- || echo "http://localhost")
echo ""
echo "Services démarrés. Accès :"
echo "  Application : ${PUBLIC_URL}"
echo "  API docs    : ${PUBLIC_URL}/docs"
echo ""
echo "Monitoring (optionnel) :"
echo "  docker compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d"
