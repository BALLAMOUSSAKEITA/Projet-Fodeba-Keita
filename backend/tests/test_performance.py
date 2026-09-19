"""Tests performance — latence API (< 2 s) et bulletin PDF (< 5 s)."""

import time

import pytest

MAX_API_SECONDS = 2.0
MAX_BULLETIN_SECONDS = 5.0


async def _setup_bulletin(client, admin_token):
    classes = (await client.get("/api/v1/parametrage/classes", headers={"Authorization": f"Bearer {admin_token}"})).json()
    classe = classes[0]
    matieres = (await client.get("/api/v1/parametrage/matieres", headers={"Authorization": f"Bearer {admin_token}"})).json()
    annee = (await client.get("/api/v1/parametrage/annees-scolaires/active", headers={"Authorization": f"Bearer {admin_token}"})).json()
    periodes = (
        await client.get(
            f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    types = (await client.get("/api/v1/notes/types-evaluation", headers={"Authorization": f"Bearer {admin_token}"})).json()

    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Perf",
                "prenoms": "Test",
                "sexe": "M",
                "date_naissance": "2015-01-01",
                "niveau_id": classe["niveau_id"],
                "tuteurs": [{"type": "pere", "nom": "P", "prenoms": "T", "telephone": "+224621888888"}],
            },
        )
    ).json()
    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    ev = (
        await client.post(
            "/api/v1/notes/evaluations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "libelle": "Perf Eval",
                "classe_id": classe["id"],
                "matiere_id": matieres[0]["id"],
                "periode_id": periodes[0]["id"],
                "type_evaluation_id": types[0]["id"],
            },
        )
    ).json()
    await client.put(
        f"/api/v1/notes/evaluations/{ev['id']}/notes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 12}]},
    )
    return eleve, periodes[0]


@pytest.mark.asyncio
async def test_performance_liste_eleves(client, admin_token):
    start = time.perf_counter()
    r = await client.get("/api/v1/eleves?limit=50", headers={"Authorization": f"Bearer {admin_token}"})
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < MAX_API_SECONDS, f"Liste élèves trop lente : {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_performance_dashboard_kpi(client, admin_token):
    start = time.perf_counter()
    r = await client.get("/api/v1/rapports/dashboard/kpi", headers={"Authorization": f"Bearer {admin_token}"})
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < MAX_API_SECONDS, f"KPI trop lent : {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_performance_sync_pull(client, admin_token):
    start = time.perf_counter()
    r = await client.get("/api/v1/sync/pull", headers={"Authorization": f"Bearer {admin_token}"})
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < MAX_API_SECONDS, f"Sync pull trop lent : {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_performance_bulletin_pdf(client, admin_token):
    eleve, periode = await _setup_bulletin(client, admin_token)
    start = time.perf_counter()
    r = await client.get(
        f"/api/v1/bulletins/eleve/{eleve['id']}/periodes/{periode['id']}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < MAX_BULLETIN_SECONDS, f"Bulletin PDF trop lent : {elapsed:.2f}s"
