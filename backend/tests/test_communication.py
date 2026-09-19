import pytest


@pytest.fixture
async def parent_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "parent@fodebakeita.gn", "password": "parent123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_annonces_et_modeles(client, admin_token):
    r = await client.get(
        "/api/v1/communication/annonces",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r2 = await client.get(
        "/api/v1/communication/modeles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert len(r2.json()) >= 2


@pytest.mark.asyncio
async def test_create_and_publish_annonce(client, admin_token):
    annonce = (
        await client.post(
            "/api/v1/communication/annonces?publier=true",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "titre": "Test annonce Sprint 15",
                "contenu": "Contenu de test pour validation du sprint communication.",
                "audience": "parents",
            },
        )
    ).json()
    assert annonce["statut"] == "publiee"

    listed = (
        await client.get(
            "/api/v1/communication/annonces?publiees_seulement=true&audience=parents",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    assert any(a["id"] == annonce["id"] for a in listed)


@pytest.mark.asyncio
async def test_envoi_message_simule(client, admin_token):
    modeles = (
        await client.get(
            "/api/v1/communication/modeles",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    r = await client.post(
        "/api/v1/communication/envoyer",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "modele_id": modeles[0]["id"],
            "canal": "sms",
            "destinataire": "+224621111111",
            "sujet": "Test",
            "corps": "Test",
        },
    )
    assert r.status_code == 201
    assert r.json()["statut"] == "simule"

    hist = (
        await client.get(
            "/api/v1/communication/historique",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    assert len(hist) >= 1


@pytest.mark.asyncio
async def test_portail_parent(client, parent_token):
    enfants = (
        await client.get(
            "/api/v1/portail/mes-enfants",
            headers={"Authorization": f"Bearer {parent_token}"},
        )
    ).json()
    assert len(enfants) >= 1

    eleve_id = enfants[0]["eleve_id"]
    resume = (
        await client.get(
            f"/api/v1/portail/enfants/{eleve_id}/resume",
            headers={"Authorization": f"Bearer {parent_token}"},
        )
    ).json()
    assert resume["eleve_id"] == eleve_id
    assert float(resume["total_du"]) >= 0
    assert len(resume["annonces"]) >= 1


@pytest.mark.asyncio
async def test_portail_acces_refuse(client, parent_token, admin_token):
    niveau = (
        await client.get(
            "/api/v1/parametrage/niveaux",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    n3a = next(n for n in niveau if n["code"] == "3A")

    autre = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Bah",
                "prenoms": "Oumar",
                "sexe": "M",
                "date_naissance": "2015-01-01",
                "niveau_id": n3a["id"],
                "tuteurs": [
                    {
                        "type": "pere",
                        "nom": "Bah",
                        "prenoms": "Oumar",
                        "telephone": "+224629999999",
                    }
                ],
            },
        )
    ).json()

    r = await client.get(
        f"/api/v1/portail/enfants/{autre['id']}/resume",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert r.status_code == 403
