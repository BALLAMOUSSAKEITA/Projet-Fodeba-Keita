import pytest


@pytest.mark.asyncio
async def test_list_creneaux(client, admin_token):
    r = await client.get(
        "/api/v1/emploi-du-temps/creneaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 6


@pytest.mark.asyncio
async def test_grille_classe(client, admin_token):
    classes = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    classe_id = classes.json()[0]["id"]
    r = await client.get(
        f"/api/v1/emploi-du-temps/classe/{classe_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["lignes"]) >= 6
    assert len(data["jours"]) == 5


@pytest.mark.asyncio
async def test_create_seance(client, admin_token):
    classes = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    matieres = await client.get(
        "/api/v1/parametrage/matieres",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    personnel = await client.get(
        "/api/v1/personnel?categorie=enseignant",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    creneaux = await client.get(
        "/api/v1/emploi-du-temps/creneaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    classe = classes.json()[1]
    r = await client.post(
        "/api/v1/emploi-du-temps/seances",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "classe_id": classe["id"],
            "creneau_id": creneaux.json()[1]["id"],
            "jour_semaine": 1,
            "matiere_id": matieres.json()[0]["id"],
            "personnel_id": personnel.json()["items"][0]["id"],
        },
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_conflit_enseignant(client, admin_token):
    classes = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    matieres = await client.get(
        "/api/v1/parametrage/matieres",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    personnel = await client.get(
        "/api/v1/personnel?categorie=enseignant",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    creneaux = await client.get(
        "/api/v1/emploi-du-temps/creneaux",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    pid = personnel.json()["items"][0]["id"]
    cid = creneaux.json()[0]["id"]
    c0 = classes.json()[0]
    c1 = classes.json()[1] if len(classes.json()) > 1 else c0

    await client.post(
        "/api/v1/emploi-du-temps/seances",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "classe_id": c0["id"],
            "creneau_id": cid,
            "jour_semaine": 2,
            "matiere_id": matieres.json()[0]["id"],
            "personnel_id": pid,
        },
    )
    r = await client.post(
        "/api/v1/emploi-du-temps/seances",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "classe_id": c1["id"],
            "creneau_id": cid,
            "jour_semaine": 2,
            "matiere_id": matieres.json()[1]["id"],
            "personnel_id": pid,
        },
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_grille_enseignant(client, admin_token):
    personnel = await client.get(
        "/api/v1/personnel?categorie=enseignant",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    pid = personnel.json()["items"][0]["id"]
    r = await client.get(
        f"/api/v1/emploi-du-temps/enseignant/{pid}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_export_pdf(client, admin_token):
    classes = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    classe_id = classes.json()[0]["id"]
    r = await client.get(
        f"/api/v1/emploi-du-temps/classe/{classe_id}/export/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_teacher_can_view_edt(client, teacher_token):
    r = await client.get(
        "/api/v1/emploi-du-temps/creneaux",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r.status_code == 200
