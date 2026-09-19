import pytest


async def _setup_evaluation(client, admin_token):
    classes = (await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    matieres = (await client.get(
        "/api/v1/parametrage/matieres",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    annee = (await client.get(
        "/api/v1/parametrage/annees-scolaires/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    periodes = (await client.get(
        f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    types = (await client.get(
        "/api/v1/notes/types-evaluation",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()

    eleve = (await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "NotesTest",
            "prenoms": "Eleve",
            "sexe": "M",
            "date_naissance": "2015-03-01",
            "niveau_id": classes[0]["niveau_id"],
            "tuteurs": [{"type": "pere", "nom": "T", "prenoms": "P", "telephone": "+224621000099"}],
        },
    )).json()

    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classes[0]["id"]},
    )

    ev = (await client.post(
        "/api/v1/notes/evaluations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "libelle": "Devoir 1",
            "classe_id": classes[0]["id"],
            "matiere_id": matieres[0]["id"],
            "periode_id": periodes[0]["id"],
            "type_evaluation_id": types[0]["id"],
        },
    )).json()

    return ev, eleve, classes[0], periodes[0]


@pytest.mark.asyncio
async def test_types_evaluation(client, admin_token):
    r = await client.get(
        "/api/v1/notes/types-evaluation",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 3


@pytest.mark.asyncio
async def test_saisie_notes(client, admin_token):
    ev, eleve, _, _ = await _setup_evaluation(client, admin_token)

    r = await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 15.5}]},
    )
    assert r.status_code == 200
    assert r.json()["eleves"][0]["note"]["valeur"] == "15.50" or r.json()["eleves"][0]["note"]["valeur"] == 15.5


@pytest.mark.asyncio
async def test_note_absent(client, admin_token):
    ev, eleve, _, _ = await _setup_evaluation(client, admin_token)

    r = await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "is_absent": True}]},
    )
    assert r.status_code == 200
    assert r.json()["eleves"][0]["note"]["is_absent"] is True


@pytest.mark.asyncio
async def test_note_hors_bareme(client, admin_token):
    ev, eleve, _, _ = await _setup_evaluation(client, admin_token)

    r = await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 25}]},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_moyennes_et_rang(client, admin_token):
    ev, eleve, classe, periode = await _setup_evaluation(client, admin_token)
    await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 14}]},
    )

    r = await client.get(
        f"/api/v1/notes/classes/{classe['id']}/periodes/{periode['id']}/moyennes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["eleves"]) >= 1
    assert data["eleves"][0]["moyenne_generale"] is not None


@pytest.mark.asyncio
async def test_verrouillage(client, admin_token):
    ev, eleve, classe, periode = await _setup_evaluation(client, admin_token)

    r = await client.post(
        f"/api/v1/notes/classes/{classe['id']}/periodes/{periode['id']}/valider",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["verrouille"] is True

    r2 = await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 10}]},
    )
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_teacher_can_modify(client, teacher_token, admin_token):
    ev, eleve, _, _ = await _setup_evaluation(client, admin_token)
    r = await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 12}]},
    )
    assert r.status_code == 200
