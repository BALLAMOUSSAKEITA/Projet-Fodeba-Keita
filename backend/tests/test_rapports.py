from datetime import date

import pytest


@pytest.mark.asyncio
async def test_dashboard_kpi(client, admin_token):
    r = await client.get(
        "/api/v1/rapports/dashboard/kpi",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_eleves"] >= 0
    assert "annee_libelle" in data


@pytest.mark.asyncio
async def test_rapport_effectifs(client, admin_token):
    r = await client.get(
        "/api/v1/rapports/effectifs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert "stats" in r.json()
    assert "par_classe" in r.json()


@pytest.mark.asyncio
async def test_rapport_financier(client, admin_token):
    annee = (
        await client.get(
            "/api/v1/parametrage/annees-scolaires/active",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    debut = annee["date_debut"]
    fin = date.today().isoformat()

    r = await client.get(
        f"/api/v1/rapports/financier?date_debut={debut}&date_fin={fin}&annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert float(r.json()["total_recettes"]) >= 0


@pytest.mark.asyncio
async def test_rapport_pedagogique_et_graphiques(client, admin_token):
    r1 = await client.get(
        "/api/v1/rapports/pedagogique",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r1.status_code == 200
    assert "classes" in r1.json()

    r2 = await client.get(
        "/api/v1/rapports/graphiques",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert "effectifs_par_niveau" in r2.json()


@pytest.mark.asyncio
async def test_statistiques_annuelles_et_exports(client, admin_token):
    r = await client.get(
        "/api/v1/rapports/annuel",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["etablissement"]

    csv_r = await client.get(
        "/api/v1/rapports/export/csv?type=effectifs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert csv_r.status_code == 200
    assert "text/csv" in csv_r.headers["content-type"]

    pdf_r = await client.get(
        "/api/v1/rapports/export/pdf?type=annuel",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pdf_r.status_code == 200
    assert pdf_r.headers["content-type"] == "application/pdf"
