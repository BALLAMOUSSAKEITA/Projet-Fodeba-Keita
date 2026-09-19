import csv

import pytest
from sqlalchemy import select

from app.models.parametrage import Niveau
from app.services import migration_service


@pytest.mark.asyncio
async def test_import_eleves_csv(db_session, tmp_path):
    csv_path = tmp_path / "eleves.csv"
    result = await db_session.execute(select(Niveau).limit(1))
    niveau = result.scalar_one()

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "nom", "prenoms", "sexe", "date_naissance", "niveau_code",
                "classe_nom", "tuteur_type", "tuteur_nom", "tuteur_prenoms", "tuteur_telephone",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "nom": "Import",
            "prenoms": "Test",
            "sexe": "M",
            "date_naissance": "2015-01-01",
            "niveau_code": niveau.code,
            "classe_nom": "",
            "tuteur_type": "pere",
            "tuteur_nom": "Import",
            "tuteur_prenoms": "Papa",
            "tuteur_telephone": "+224621555555",
        })

    report = await migration_service.import_eleves_csv(db_session, csv_path)
    assert report.created == 1
    assert not report.errors

    verification = await migration_service.verify_migration(db_session)
    assert verification["total_eleves"] >= 1


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "sgep_up" in r.text
    assert "sgep_eleves_total" in r.text
