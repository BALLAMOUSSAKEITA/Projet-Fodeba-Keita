import pytest


async def _get_niveau_3a(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/niveaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return next(n for n in response.json() if n["code"] == "3A")


@pytest.mark.asyncio
async def test_create_eleve_with_matricule(client, admin_token):
    niveau = await _get_niveau_3a(client, admin_token)
    response = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Diallo",
            "prenoms": "Mamadou Alpha",
            "sexe": "M",
            "date_naissance": "2015-03-12",
            "lieu_naissance": "Conakry",
            "nationalite": "Guinéenne",
            "adresse": "Ratoma",
            "niveau_id": niveau["id"],
            "tuteurs": [
                {
                    "type": "pere",
                    "nom": "Diallo",
                    "prenoms": "Ibrahima",
                    "telephone": "+224621111111",
                    "profession": "Commerçant",
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["matricule"].startswith("2025-P3-")
    assert data["nom"] == "Diallo"
    assert len(data["tuteurs"]) == 1
    assert len(data["inscriptions"]) == 1
    assert data["inscriptions"][0]["type"] == "nouvelle"


@pytest.mark.asyncio
async def test_list_eleves_with_search(client, admin_token):
    niveau = await _get_niveau_3a(client, admin_token)
    await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Camara",
            "prenoms": "Fatoumata",
            "sexe": "F",
            "date_naissance": "2016-07-20",
            "niveau_id": niveau["id"],
            "tuteurs": [
                {
                    "type": "mere",
                    "nom": "Camara",
                    "prenoms": "Aissatou",
                    "telephone": "+224622222222",
                }
            ],
        },
    )

    response = await client.get(
        "/api/v1/eleves?search=Camara",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Camara" in e["nom"] for e in data["items"])


@pytest.mark.asyncio
async def test_reinscription_eleve(client, admin_token):
    niveau_3a = await _get_niveau_3a(client, admin_token)
    niveaux = await client.get(
        "/api/v1/parametrage/niveaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    niveau_4a = next(n for n in niveaux.json() if n["code"] == "4A")

    create = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Bah",
            "prenoms": "Oumar",
            "sexe": "M",
            "date_naissance": "2014-01-15",
            "niveau_id": niveau_3a["id"],
            "tuteurs": [
                {"type": "pere", "nom": "Bah", "prenoms": "Sekou", "telephone": "+224623333333"}
            ],
        },
    )
    eleve_id = create.json()["id"]
    matricule = create.json()["matricule"]

    reinscrire = await client.post(
        f"/api/v1/eleves/{eleve_id}/reinscrire",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"niveau_id": niveau_4a["id"]},
    )
    assert reinscrire.status_code == 200
    assert reinscrire.json()["matricule"] == matricule
    assert len(reinscrire.json()["inscriptions"]) == 1


@pytest.mark.asyncio
async def test_get_eleve_detail(client, admin_token):
    niveau = await _get_niveau_3a(client, admin_token)
    create = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Soumah",
            "prenoms": "Kadiatou",
            "sexe": "F",
            "date_naissance": "2015-11-05",
            "niveau_id": niveau["id"],
            "tuteurs": [
                {"type": "tuteur", "nom": "Soumah", "prenoms": "Mariama", "telephone": "+224624444444"}
            ],
        },
    )
    eleve_id = create.json()["id"]

    response = await client.get(
        f"/api/v1/eleves/{eleve_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["prenoms"] == "Kadiatou"


@pytest.mark.asyncio
async def test_rbac_eleves_forbidden(client, teacher_token):
    response = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "nom": "Test",
            "prenoms": "Test",
            "sexe": "M",
            "date_naissance": "2015-01-01",
            "niveau_id": "00000000-0000-0000-0000-000000000001",
            "tuteurs": [
                {"type": "pere", "nom": "Test", "prenoms": "Test", "telephone": "+224620000000"}
            ],
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_teacher_can_view_eleves(client, teacher_token, admin_token):
    niveau = await _get_niveau_3a(client, admin_token)
    await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Kourouma",
            "prenoms": "Aboubacar",
            "sexe": "M",
            "date_naissance": "2015-05-10",
            "niveau_id": niveau["id"],
            "tuteurs": [
                {"type": "pere", "nom": "Kourouma", "prenoms": "Ali", "telephone": "+224625555555"}
            ],
        },
    )

    response = await client.get(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1
