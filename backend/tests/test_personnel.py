import pytest


@pytest.mark.asyncio
async def test_list_personnel(client, admin_token):
    r = await client.get(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 3
    assert any(p["categorie"] == "enseignant" for p in data["items"])


@pytest.mark.asyncio
async def test_create_enseignant(client, admin_token):
    r = await client.post(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Soumah",
            "prenoms": "Aissatou",
            "sexe": "F",
            "telephone": "+224621111111",
            "categorie": "enseignant",
            "specialite": "Mathématiques",
        },
    )
    assert r.status_code == 201
    assert r.json()["matricule"].startswith("ENS-")


@pytest.mark.asyncio
async def test_create_non_enseignant(client, admin_token):
    r = await client.post(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Kourouma",
            "prenoms": "Alpha",
            "sexe": "M",
            "telephone": "+224621111112",
            "categorie": "non_enseignant",
            "fonction": "Comptable",
        },
    )
    assert r.status_code == 201
    assert r.json()["matricule"].startswith("PER-")


@pytest.mark.asyncio
async def test_add_diplome_and_contrat(client, admin_token):
    create = await client.post(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Barry",
            "prenoms": "Oumar",
            "sexe": "M",
            "telephone": "+224621111113",
            "categorie": "enseignant",
        },
    )
    pid = create.json()["id"]

    r = await client.post(
        f"/api/v1/personnel/{pid}/diplomes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"libelle": "CAPES", "niveau": "Master"},
    )
    assert r.status_code == 201
    assert len(r.json()["diplomes"]) == 1

    r2 = await client.post(
        f"/api/v1/personnel/{pid}/contrats",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type_contrat": "cdd",
            "date_debut": "2025-09-01",
            "date_fin": "2026-06-30",
            "salaire_mensuel": 2500000,
        },
    )
    assert r2.status_code == 201
    assert len(r2.json()["contrats"]) == 1


@pytest.mark.asyncio
async def test_affectation_and_titulaire(client, admin_token):
    classes = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    matieres = await client.get(
        "/api/v1/parametrage/matieres",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    classe = classes.json()[0]
    matiere = matieres.json()[0]

    create = await client.post(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Sylla",
            "prenoms": "Mariama",
            "sexe": "F",
            "telephone": "+224621111114",
            "categorie": "enseignant",
        },
    )
    pid = create.json()["id"]

    r = await client.post(
        f"/api/v1/personnel/{pid}/affectations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"], "matiere_id": matiere["id"]},
    )
    assert r.status_code == 201
    assert len(r.json()["affectations"]) >= 1

    r2 = await client.post(
        f"/api/v1/personnel/{pid}/titulaire",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    assert r2.status_code == 200
    assert len(r2.json()["classes_titulaire"]) >= 1


@pytest.mark.asyncio
async def test_conge_absence(client, admin_token):
    listing = await client.get(
        "/api/v1/personnel?categorie=enseignant",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    pid = listing.json()["items"][0]["id"]

    r = await client.post(
        f"/api/v1/personnel/{pid}/conges",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type": "conge",
            "date_debut": "2025-12-20",
            "date_fin": "2026-01-05",
            "motif": "Congés de fin d'année",
        },
    )
    assert r.status_code == 201
    assert len(r.json()["conges"]) >= 1


@pytest.mark.asyncio
async def test_rbac_personnel_forbidden(client, teacher_token):
    r = await client.get(
        "/api/v1/personnel",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r.status_code == 403
