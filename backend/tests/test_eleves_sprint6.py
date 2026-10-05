import pytest

from tests.helpers import default_eleve_create_payload, get_classe_for_niveau, get_niveau_by_code


async def _niveau(client, token, code):
    return await get_niveau_by_code(client, token, code)


async def _classe(client, token, niveau_code):
    niveau = await _niveau(client, token, niveau_code)
    return await get_classe_for_niveau(client, token, niveau["id"])


async def _create_eleve(client, token, nom="Test", niveau_code="3A"):
    payload = await default_eleve_create_payload(client, token, niveau_code, nom=nom)
    payload["tuteurs"] = [{"type": "pere", "nom": nom, "prenoms": "Papa", "telephone": "+224621000000"}]
    r = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert r.status_code == 201
    return r.json()


@pytest.mark.asyncio
async def test_affecter_classe(client, admin_token):
    eleve = await _create_eleve(client, admin_token, "Affecte")
    classe = await _classe(client, admin_token, "3A")

    r = await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    assert r.status_code == 200
    assert r.json()["inscriptions"][0]["classe_id"] == classe["id"]


@pytest.mark.asyncio
async def test_classe_effectifs(client, admin_token):
    r = await client.get(
        "/api/v1/classes/effectifs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 10


@pytest.mark.asyncio
async def test_transfert_sortant(client, admin_token):
    eleve = await _create_eleve(client, admin_token, "Sortant")
    r = await client.post(
        f"/api/v1/eleves/{eleve['id']}/transfert-sortant",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"ecole_destination": "École ABC", "motif": "Déménagement"},
    )
    assert r.status_code == 200
    assert r.json()["statut"] == "inactif"


@pytest.mark.asyncio
async def test_historique(client, admin_token):
    eleve = await _create_eleve(client, admin_token, "Historique")
    r = await client.get(
        f"/api/v1/eleves/{eleve['id']}/historique",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()["inscriptions"]) >= 1


@pytest.mark.asyncio
async def test_stats_effectifs(client, admin_token):
    await _create_eleve(client, admin_token, "Stats")
    r = await client.get(
        "/api/v1/eleves/statistiques/effectifs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["total_eleves"] >= 1


@pytest.mark.asyncio
async def test_attestation_pdf(client, admin_token):
    eleve = await _create_eleve(client, admin_token, "Attest")
    r = await client.get(
        f"/api/v1/eleves/{eleve['id']}/attestation/scolarite",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 100


@pytest.mark.asyncio
async def test_liste_classe_pdf(client, admin_token):
    eleve = await _create_eleve(client, admin_token, "ListePDF")
    classe = await _classe(client, admin_token, "3A")
    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    r = await client.get(
        f"/api/v1/classes/{classe['id']}/liste-pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
