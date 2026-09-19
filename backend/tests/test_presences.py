from datetime import date, timedelta

import pytest


async def _get_classe_eleve(client, admin_token):
    classes = (await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    classe = classes[0]

    eleve = (await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "PresenceTest",
            "prenoms": "Eleve",
            "sexe": "M",
            "date_naissance": "2015-03-01",
            "niveau_id": classe["niveau_id"],
            "tuteurs": [{"type": "pere", "nom": "T", "prenoms": "P", "telephone": "+224621000088"}],
        },
    )).json()

    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    return classe, eleve


@pytest.mark.asyncio
async def test_appel_journalier(client, admin_token):
    classe, eleve = await _get_classe_eleve(client, admin_token)
    today = date.today().isoformat()

    r = await client.get(
        f"/api/v1/presences/classes/{classe['id']}/appels?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["classe_id"] == classe["id"]
    assert len(data["eleves"]) >= 1

    r2 = await client.put(
        f"/api/v1/presences/classes/{classe['id']}/appels?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "presences": [
                {"eleve_id": eleve["id"], "statut": "absent", "motif": "Maladie"},
            ],
        },
    )
    assert r2.status_code == 200
    row = next(e for e in r2.json()["eleves"] if e["eleve_id"] == eleve["id"])
    assert row["statut"] == "absent"
    assert row["justification_statut"] == "en_attente"


@pytest.mark.asyncio
async def test_retard_et_recap(client, admin_token):
    classe, eleve = await _get_classe_eleve(client, admin_token)
    today = date.today().isoformat()

    await client.put(
        f"/api/v1/presences/classes/{classe['id']}/appels?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"presences": [{"eleve_id": eleve["id"], "statut": "retard", "retard_minutes": 20}]},
    )

    debut = (date.today() - timedelta(days=7)).isoformat()
    fin = date.today().isoformat()

    r = await client.get(
        f"/api/v1/presences/classes/{classe['id']}/recapitulatif"
        f"?date_debut={debut}&date_fin={fin}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    item = next(e for e in r.json()["eleves"] if e["eleve_id"] == eleve["id"])
    assert item["jours_retards"] == 1
    assert item["minutes_retard_total"] == 20


@pytest.mark.asyncio
async def test_justification(client, admin_token):
    classe, eleve = await _get_classe_eleve(client, admin_token)
    today = date.today().isoformat()

    saved = (await client.put(
        f"/api/v1/presences/classes/{classe['id']}/appels?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"presences": [{"eleve_id": eleve["id"], "statut": "absent", "motif": "Maladie"}]},
    )).json()
    presence_id = next(e["presence_id"] for e in saved["eleves"] if e["eleve_id"] == eleve["id"])

    r = await client.post(
        f"/api/v1/presences/presences/{presence_id}/justification",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"justification": "Certificat médical présenté", "accepter": True},
    )
    assert r.status_code == 200
    assert r.json()["statut"] == "excuse"
    assert r.json()["justification_statut"] == "acceptee"


@pytest.mark.asyncio
async def test_eleve_recap(client, admin_token):
    classe, eleve = await _get_classe_eleve(client, admin_token)
    today = date.today().isoformat()
    debut = (date.today() - timedelta(days=30)).isoformat()

    await client.put(
        f"/api/v1/presences/classes/{classe['id']}/appels?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"presences": [{"eleve_id": eleve["id"], "statut": "absent"}]},
    )

    r = await client.get(
        f"/api/v1/presences/eleve/{eleve['id']}/recapitulatif"
        f"?date_debut={debut}&date_fin={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["jours_absents"] >= 1


@pytest.mark.asyncio
async def test_incident_disciplinaire(client, admin_token):
    classe, eleve = await _get_classe_eleve(client, admin_token)
    today = date.today().isoformat()

    r = await client.post(
        "/api/v1/presences/discipline",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "classe_id": classe["id"],
            "date": today,
            "type": "avertissement",
            "description": "Bavardage répété en cours de mathématiques",
            "sanction": "Avertissement écrit",
        },
    )
    assert r.status_code == 201
    assert r.json()["type"] == "avertissement"

    r2 = await client.get(
        f"/api/v1/presences/discipline?classe_id={classe['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


@pytest.mark.asyncio
async def test_enseignants_absences(client, admin_token):
    today = date.today().isoformat()
    r = await client.get(
        f"/api/v1/presences/enseignants/absences?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)
