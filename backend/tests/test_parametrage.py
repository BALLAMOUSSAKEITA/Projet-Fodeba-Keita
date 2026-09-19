import pytest


@pytest.mark.asyncio
async def test_get_parametrage_statut(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/statut",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["etablissement_configure"] is True
    assert data["annee_active"] is True
    assert data["niveaux_count"] == 9
    assert data["pret_pour_inscriptions"] is True


@pytest.mark.asyncio
async def test_get_etablissement(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/etablissement",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Fodeba Keita" in response.json()["nom"]
    assert response.json()["devise_principale"] == "GNF"


@pytest.mark.asyncio
async def test_get_annee_active(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/annees-scolaires/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["libelle"] == "2025-2026"
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_list_niveaux(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/niveaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 9


@pytest.mark.asyncio
async def test_list_classes(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 10


@pytest.mark.asyncio
async def test_list_matieres(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/matieres",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 7


@pytest.mark.asyncio
async def test_list_types_frais(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/types-frais",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 7


@pytest.mark.asyncio
async def test_list_referentiels(client, admin_token):
    response = await client.get(
        "/api/v1/parametrage/referentiels/region",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 8


@pytest.mark.asyncio
async def test_update_etablissement(client, admin_token):
    response = await client.patch(
        "/api/v1/parametrage/etablissement",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"telephone": "+224629999999"},
    )
    assert response.status_code == 200
    assert response.json()["telephone"] == "+224629999999"


@pytest.mark.asyncio
async def test_rbac_settings_forbidden(client, teacher_token):
    response = await client.patch(
        "/api/v1/parametrage/etablissement",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"telephone": "+224000000000"},
    )
    assert response.status_code == 403
