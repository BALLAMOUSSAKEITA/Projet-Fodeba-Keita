#!/usr/bin/env bash
# Sauvegarde PostgreSQL SGEP — Sprint 17
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$ROOT/backend/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5432}"
USER="${POSTGRES_USER:-sgep}"
DB="${POSTGRES_DB:-sgep_db}"
export PGPASSWORD="${POSTGRES_PASSWORD:-sgep_dev_password}"

OUT="$BACKUP_DIR/sgep_${TIMESTAMP}.sql.gz"
pg_dump -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" | gzip > "$OUT"
echo "Sauvegarde créée: $OUT"
