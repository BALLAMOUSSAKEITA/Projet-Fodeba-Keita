from datetime import UTC, datetime, timedelta

import pytest


async def _get_setup(client, admin_token):
    classes = (
        await client.get(
            "/api/v1/parametrage/classes",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    annee = (
        await client.get(
            "/api/v1/parametrage/annees-scolaires/active",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    periodes = (
        await client.get(
            f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    matieres = (
        await client.get(
            "/api/v1/parametrage/matieres",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    types_eval = (
        await client.get(
            "/api/v1/notes/types-evaluation",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    return classes[0], periodes[0], matieres[0], types_eval[0]


@pytest.mark.asyncio
async def test_sync_pull_bundle(client, admin_token):
    r = await client.get(
        "/api/v1/sync/pull",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "server_time" in data
    assert isinstance(data["eleves"], list)
    assert isinstance(data["classes"], list)
    assert data["eleves_total"] >= 0


@pytest.mark.asyncio
async def test_sync_push_notes(client, admin_token):
    classe, periode, matiere, type_eval = await _get_setup(client, admin_token)

    evaluation = (
        await client.post(
            "/api/v1/notes/evaluations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "libelle": "Sync Test",
                "classe_id": classe["id"],
                "matiere_id": matiere["id"],
                "periode_id": periode["id"],
                "type_evaluation_id": type_eval["id"],
            },
        )
    ).json()

    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Sync",
                "prenoms": "Notes",
                "sexe": "M",
                "date_naissance": "2015-03-01",
                "niveau_id": classe["niveau_id"],
                "tuteurs": [{"type": "pere", "nom": "Sync", "prenoms": "Papa", "telephone": "+224621222222"}],
            },
        )
    ).json()
    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )

    grille = (
        await client.get(
            f"/api/v1/notes/evaluations/{evaluation['id']}/grille",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    eleve_row = next(e for e in grille["eleves"] if e["eleve_id"] == eleve["id"])

    now = datetime.now(UTC).isoformat()
    push = await client.post(
        "/api/v1/sync/push",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "operations": [
                {
                    "client_id": "note-sync-001",
                    "entity_type": "notes",
                    "client_updated_at": now,
                    "payload": {
                        "evaluation_id": evaluation["id"],
                        "data": {
                            "notes": [
                                {
                                    "eleve_id": eleve_row["eleve_id"],
                                    "valeur": 14,
                                    "is_absent": False,
                                }
                            ]
                        },
                    },
                }
            ]
        },
    )
    assert push.status_code == 200
    body = push.json()
    assert body["applied"] == 1
    assert body["results"][0]["status"] == "applied"


@pytest.mark.asyncio
async def test_sync_push_presence(client, admin_token):
    classe, _, _, _ = await _get_setup(client, admin_token)
    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Sync",
                "prenoms": "Presence",
                "sexe": "F",
                "date_naissance": "2015-04-01",
                "niveau_id": classe["niveau_id"],
                "tuteurs": [{"type": "mere", "nom": "Sync", "prenoms": "Maman", "telephone": "+224621333333"}],
            },
        )
    ).json()
    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )

    appel = (
        await client.get(
            f"/api/v1/presences/classes/{classe['id']}/appels?date=2025-10-01",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    eleve_row = next(e for e in appel["eleves"] if e["eleve_id"] == eleve["id"])
    now = datetime.now(UTC).isoformat()

    push = await client.post(
        "/api/v1/sync/push",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "operations": [
                {
                    "client_id": "presence-sync-001",
                    "entity_type": "presence",
                    "client_updated_at": now,
                    "payload": {
                        "classe_id": classe["id"],
                        "appel_date": "2025-10-01",
                        "data": {
                            "presences": [
                                {
                                    "eleve_id": eleve_row["eleve_id"],
                                    "statut": "absent",
                                    "motif": "Sync offline",
                                }
                            ]
                        },
                    },
                }
            ]
        },
    )
    assert push.status_code == 200
    assert push.json()["applied"] == 1


@pytest.mark.asyncio
async def test_sync_push_paiement_idempotent(client, admin_token):
    annee = (
        await client.get(
            "/api/v1/parametrage/annees-scolaires/active",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    niveau = next(
        n
        for n in (
            await client.get("/api/v1/parametrage/niveaux", headers={"Authorization": f"Bearer {admin_token}"})
        ).json()
        if n["code"] == "3A"
    )
    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Sync",
                "prenoms": "Paiement",
                "sexe": "M",
                "date_naissance": "2015-03-01",
                "niveau_id": niveau["id"],
                "tuteurs": [{"type": "pere", "nom": "Sync", "prenoms": "Papa", "telephone": "+224621111111"}],
            },
        )
    ).json()
    types_frais = (
        await client.get("/api/v1/parametrage/types-frais", headers={"Authorization": f"Bearer {admin_token}"})
    ).json()
    scol = next(t for t in types_frais if t["code"] == "SCOLARITE")
    now = datetime.now(UTC).isoformat()
    op = {
        "client_id": "paiement-sync-001",
        "entity_type": "paiement",
        "client_updated_at": now,
        "payload": {
            "eleve_id": eleve["id"],
            "type_frais_id": scol["id"],
            "montant": 25000,
            "mode_paiement": "especes",
            "annee_scolaire_id": annee["id"],
        },
    }

    first = await client.post(
        "/api/v1/sync/push",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"operations": [op]},
    )
    assert first.status_code == 200
    assert first.json()["results"][0]["status"] == "applied"

    second = await client.post(
        "/api/v1/sync/push",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"operations": [op]},
    )
    assert second.status_code == 200
    assert second.json()["results"][0]["status"] == "duplicate"


@pytest.mark.asyncio
async def test_sync_conflict_notes(client, admin_token):
    classe, periode, matiere, type_eval = await _get_setup(client, admin_token)

    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Conflict",
                "prenoms": "Notes",
                "sexe": "M",
                "date_naissance": "2015-03-01",
                "niveau_id": classe["niveau_id"],
                "tuteurs": [{"type": "pere", "nom": "Conflict", "prenoms": "Papa", "telephone": "+224621444444"}],
            },
        )
    ).json()
    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )

    evaluation = (
        await client.post(
            "/api/v1/notes/evaluations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "libelle": "Conflict Test",
                "classe_id": classe["id"],
                "matiere_id": matiere["id"],
                "periode_id": periode["id"],
                "type_evaluation_id": type_eval["id"],
            },
        )
    ).json()
    grille = (
        await client.get(
            f"/api/v1/notes/evaluations/{evaluation['id']}/grille",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    eleve_row = next(e for e in grille["eleves"] if e["eleve_id"] == eleve["id"])

    await client.put(
        f"/api/v1/notes/evaluations/{evaluation['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve_row["eleve_id"], "valeur": 16, "is_absent": False}]},
    )

    stale = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
    push = await client.post(
        "/api/v1/sync/push",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "operations": [
                {
                    "client_id": "note-conflict-001",
                    "entity_type": "notes",
                    "client_updated_at": stale,
                    "resolve_strategy": "server_wins",
                    "payload": {
                        "evaluation_id": evaluation["id"],
                        "data": {
                            "notes": [
                                {
                                    "eleve_id": eleve_row["eleve_id"],
                                    "valeur": 10,
                                    "is_absent": False,
                                }
                            ]
                        },
                    },
                }
            ]
        },
    )
    assert push.status_code == 200
    assert push.json()["conflicts"] == 1
    assert push.json()["results"][0]["status"] == "conflict"
