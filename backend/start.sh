#!/bin/sh
set -e

echo "=== Migrations Alembic ==="
alembic upgrade head

echo "=== Démarrage API (port ${PORT:-8000}) ==="
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
