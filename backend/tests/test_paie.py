from datetime import date

import pytest


@pytest.mark.asyncio
async def test_periode_et_generation(client, admin_token):
    r = await client.post(
        "/api/v1/paie/periodes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"annee": 2025, "mois": 10},
    )
    assert r.status_code == 201
    periode = r.json()

    gen = await client.post(
        f"/api/v1/paie/periodes/{periode['id']}/generer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert gen.status_code == 200
    bulletins = gen.json()
    assert len(bulletins) >= 1
    assert float(bulletins[0]["net_a_payer"]) > 0


@pytest.mark.asyncio
async def test_bulletin_pdf_et_paiement(client, admin_token):
    periodes = (await client.get(
        "/api/v1/paie/periodes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    periode = periodes[0]

    await client.post(
        f"/api/v1/paie/periodes/{periode['id']}/generer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    bulletins = (await client.get(
        f"/api/v1/paie/bulletins?periode_paie_id={periode['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    bulletin = bulletins[0]

    pdf = await client.get(
        f"/api/v1/paie/bulletins/{bulletin['id']}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"

    val = await client.post(
        f"/api/v1/paie/bulletins/{bulletin['id']}/valider",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert val.status_code == 200

    pay = await client.post(
        f"/api/v1/paie/bulletins/{bulletin['id']}/payer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pay.status_code == 200
    assert pay.json()["statut"] == "paye"


@pytest.mark.asyncio
async def test_avance_salaire(client, admin_token):
    personnel = (await client.get(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()["items"][0]

    r = await client.post(
        "/api/v1/paie/avances",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "personnel_id": personnel["id"],
            "montant": 200000,
            "date_avance": date.today().isoformat(),
            "motif": "Urgence familiale",
        },
    )
    assert r.status_code == 201
    assert r.json()["statut"] == "active"


@pytest.mark.asyncio
async def test_masse_salariale(client, admin_token):
    periodes = (await client.get(
        "/api/v1/paie/periodes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()

    r = await client.get(
        f"/api/v1/paie/masse-salariale?periode_paie_id={periodes[0]['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["nombre_bulletins"] >= 0
    assert "total_brut" in data


@pytest.mark.asyncio
async def test_mes_bulletins_enseignant(client, teacher_token):
    r = await client.get(
        "/api/v1/paie/mes-bulletins",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)
