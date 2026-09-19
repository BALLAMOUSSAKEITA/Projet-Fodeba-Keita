#!/usr/bin/env bash
# Synchronisation cloud (architecture hybride)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env.production ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env.production
  set +a
fi

if [[ "${CLOUD_SYNC_ENABLED:-false}" != "true" ]]; then
  echo "Sync cloud désactivée (CLOUD_SYNC_ENABLED=false)."
  exit 0
fi

echo "=== Sauvegarde locale ==="
"$ROOT/scripts/backup-db.sh"

LATEST=$(ls -t "$ROOT/backend/backups"/sgep_*.sql.gz 2>/dev/null | head -1)
if [[ -z "$LATEST" ]]; then
  echo "Aucune sauvegarde trouvée." >&2
  exit 1
fi

REMOTE="${CLOUD_SYNC_USER}@${CLOUD_SYNC_HOST}:${CLOUD_SYNC_PATH}/"
echo "=== Envoi vers $REMOTE ==="
scp "$LATEST" "${REMOTE}sgep_latest.sql.gz"
echo "Synchronisation terminée."
