import pytest


async def _setup_notes(client, admin_token):
    classes = (await client.get("/api/v1/parametrage/classes", headers={"Authorization": f"Bearer {admin_token}"})).json()
    primaire = next(c for c in classes if c["nom"].startswith("3") or "3" in c.get("nom", ""))
    if not primaire:
        primaire = next(c for c in classes if "A" in c["nom"])
    matieres = (await client.get("/api/v1/parametrage/matieres", headers={"Authorization": f"Bearer {admin_token}"})).json()
    annee = (await client.get("/api/v1/parametrage/annees-scolaires/active", headers={"Authorization": f"Bearer {admin_token}"})).json()
    periodes = (await client.get(f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}", headers={"Authorization": f"Bearer {admin_token}"})).json()
    types = (await client.get("/api/v1/notes/types-evaluation", headers={"Authorization": f"Bearer {admin_token}"})).json()

    eleve = (await client.post("/api/v1/eleves", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "nom": "Bulletin", "prenoms": "Test", "sexe": "M", "date_naissance": "2015-01-01",
        "niveau_id": primaire["niveau_id"],
        "tuteurs": [{"type": "pere", "nom": "B", "prenoms": "P", "telephone": "+224621000088"}],
    })).json()
    await client.post(f"/api/v1/eleves/{eleve['id']}/affecter-classe", headers={"Authorization": f"Bearer {admin_token}"},
                      json={"classe_id": primaire["id"]})

    ev = (await client.post("/api/v1/notes/evaluations", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "libelle": "Compo T1", "classe_id": primaire["id"], "matiere_id": matieres[0]["id"],
        "periode_id": periodes[0]["id"], "type_evaluation_id": types[0]["id"],
    })).json()
    await client.put(f"/api/v1/notes/evaluations/{ev['id']}/notes", headers={"Authorization": f"Bearer {admin_token}"},
                     json={"notes": [{"eleve_id": eleve["id"], "valeur": 14}]})

    return eleve, primaire, periodes[0]


@pytest.mark.asyncio
async def test_bulletin_pdf(client, admin_token):
    eleve, _, periode = await _setup_notes(client, admin_token)
    r = await client.get(
        f"/api/v1/bulletins/eleve/{eleve['id']}/periodes/{periode['id']}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_stats_palmares(client, admin_token):
    eleve, classe, periode = await _setup_notes(client, admin_token)
    r = await client.get(
        f"/api/v1/bulletins/classes/{classe['id']}/periodes/{periode['id']}/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["effectif"] >= 1

    r2 = await client.get(
        f"/api/v1/bulletins/classes/{classe['id']}/periodes/{periode['id']}/palmares",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_decision_passage(client, admin_token):
    eleve, _, _ = await _setup_notes(client, admin_token)
    r = await client.post(
        "/api/v1/bulletins/decisions-passage",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"eleve_id": eleve["id"], "decision": "admis", "observation": "Bon travail"},
    )
    assert r.status_code == 201
    assert r.json()["decision"] == "admis"


@pytest.mark.asyncio
async def test_bulletin_classe_pdf(client, admin_token):
    _, classe, periode = await _setup_notes(client, admin_token)
    r = await client.get(
        f"/api/v1/bulletins/classes/{classe['id']}/periodes/{periode['id']}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_competences_maternelle(client, admin_token):
    classes = (await client.get("/api/v1/parametrage/classes", headers={"Authorization": f"Bearer {admin_token}"})).json()
    maternelle = next((c for c in classes if "PS" in c["nom"] or "Petite" in c.get("nom", "")), classes[0])
    annee = (await client.get("/api/v1/parametrage/annees-scolaires/active", headers={"Authorization": f"Bearer {admin_token}"})).json()
    periodes = (await client.get(f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}", headers={"Authorization": f"Bearer {admin_token}"})).json()

    r = await client.get(
        f"/api/v1/bulletins/classes/{maternelle['id']}/periodes/{periodes[0]['id']}/competences",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    if r.status_code == 422:
        pytest.skip("Classe non maternelle dans le seed")
    assert r.status_code == 200
    assert len(r.json()["competences"]) >= 1
