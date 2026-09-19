#!/usr/bin/env python3
"""Import CSV élèves / personnel — migration production.

Usage:
  python scripts/import_migration.py eleves ../../data/migration/eleves.csv
  python scripts/import_migration.py personnel ../../data/migration/personnel.csv
  python scripts/import_migration.py verify
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.services import migration_service


async def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    async with AsyncSessionLocal() as db:
        if command == "verify":
            result = await migration_service.verify_migration(db)
            print("=== Vérification migration ===")
            for key, value in result.items():
                print(f"  {key}: {value}")
            return

        if len(sys.argv) < 3:
            print("Fichier CSV requis.")
            sys.exit(1)

        csv_path = Path(sys.argv[2])
        if not csv_path.exists():
            print(f"Fichier introuvable : {csv_path}")
            sys.exit(1)

        if command == "eleves":
            report = await migration_service.import_eleves_csv(db, csv_path)
        elif command == "personnel":
            report = await migration_service.import_personnel_csv(db, csv_path)
        else:
            print(f"Commande inconnue : {command}")
            sys.exit(1)

        print(f"Créés : {report.created}")
        print(f"Ignorés : {report.skipped}")
        if report.errors:
            print("Erreurs :")
            for err in report.errors:
                print(f"  - {err}")


if __name__ == "__main__":
    asyncio.run(main())
