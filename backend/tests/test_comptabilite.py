from datetime import date

import pytest


async def _setup(client, admin_token):
    cats = (await client.get(
        "/api/v1/comptabilite/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    comptes = (await client.get(
        "/api/v1/comptabilite/comptes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    annee = (await client.get(
        "/api/v1/parametrage/annees-scolaires/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    return cats[0], comptes[0], annee


@pytest.mark.asyncio
async def test_categories_et_tresorerie(client, admin_token):
    r = await client.get(
        "/api/v1/comptabilite/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 5

    r2 = await client.get(
        "/api/v1/comptabilite/tresorerie",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert float(r2.json()["total_general"]) > 0


@pytest.mark.asyncio
async def test_depense_workflow(client, admin_token):
    cat, compte, annee = await _setup(client, admin_token)

    dep = (await client.post(
        "/api/v1/comptabilite/depenses",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "categorie_id": cat["id"],
            "libelle": "Achat fournitures bureau",
            "montant": 350000,
            "date_depense": date.today().isoformat(),
            "compte_tresorerie_id": compte["id"],
        },
    )).json()

    r1 = await client.post(
        f"/api/v1/comptabilite/depenses/{dep['id']}/soumettre",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r1.status_code == 200
    assert r1.json()["statut"] == "soumise"

    r2 = await client.post(
        f"/api/v1/comptabilite/depenses/{dep['id']}/valider",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert r2.json()["statut"] == "validee"


@pytest.mark.asyncio
async def test_budget_suivi(client, admin_token):
    _, _, annee = await _setup(client, admin_token)
    r = await client.get(
        f"/api/v1/comptabilite/budget/suivi?annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["lignes"]) >= 5
    assert float(data["total_prevu"]) > 0


@pytest.mark.asyncio
async def test_journal_et_rapport(client, admin_token):
    cat, compte, annee = await _setup(client, admin_token)
    today = date.today().isoformat()
    debut = f"{date.today().year}-01-01"

    dep = (await client.post(
        "/api/v1/comptabilite/depenses",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "categorie_id": cat["id"],
            "libelle": "Test rapport",
            "montant": 100000,
            "date_depense": today,
            "compte_tresorerie_id": compte["id"],
        },
    )).json()
    await client.post(
        f"/api/v1/comptabilite/depenses/{dep['id']}/soumettre",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/comptabilite/depenses/{dep['id']}/valider",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    journal = await client.get(
        f"/api/v1/comptabilite/journal?date_debut={debut}&date_fin={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert journal.status_code == 200
    assert len(journal.json()) >= 1

    rapport = await client.get(
        f"/api/v1/comptabilite/rapports/financier?date_debut={debut}&date_fin={today}&annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert rapport.status_code == 200
    assert float(rapport.json()["total_depenses"]) >= 100000


@pytest.mark.asyncio
async def test_export_csv(client, admin_token):
    _, _, annee = await _setup(client, admin_token)
    debut = f"{date.today().year}-01-01"
    fin = date.today().isoformat()

    r = await client.get(
        f"/api/v1/comptabilite/export/csv?date_debut={debut}&date_fin={fin}&annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert len(r.content) > 50
