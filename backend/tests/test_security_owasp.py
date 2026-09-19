"""Tests sécurité — OWASP, injection, XSS, RBAC."""

import pytest

SQL_INJECTION = "' OR '1'='1"
XSS_PAYLOAD = "<script>alert('xss')</script>"


@pytest.mark.asyncio
async def test_acces_sans_token_refuse(client):
    r = await client.get("/api/v1/eleves")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_token_invalide_refuse(client):
    r = await client.get(
        "/api/v1/eleves",
        headers={"Authorization": "Bearer token.invalide"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_sql_injection_recherche_eleves(client, admin_token):
    r = await client.get(
        f"/api/v1/eleves?search={SQL_INJECTION}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json()["items"], list)


@pytest.mark.asyncio
async def test_xss_stocke_dans_nom_eleve(client, admin_token):
    niveau = (
        await client.get("/api/v1/parametrage/niveaux", headers={"Authorization": f"Bearer {admin_token}"})
    ).json()[0]
    r = await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": XSS_PAYLOAD,
            "prenoms": "TestSec",
            "sexe": "M",
            "date_naissance": "2015-06-01",
            "niveau_id": niveau["id"],
            "tuteurs": [{"type": "pere", "nom": "T", "prenoms": "P", "telephone": "+224621999999"}],
        },
    )
    assert r.status_code == 201
    assert r.json()["nom"] == XSS_PAYLOAD
    detail = (
        await client.get(
            f"/api/v1/eleves/{r.json()['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    assert detail["nom"] == XSS_PAYLOAD


@pytest.mark.asyncio
async def test_rbac_enseignant_interdit_utilisateurs(client, teacher_token):
    assert (await client.get("/api/v1/users", headers={"Authorization": f"Bearer {teacher_token}"})).status_code == 403


@pytest.mark.asyncio
async def test_rbac_enseignant_interdit_paiements(client, teacher_token):
    assert (
        await client.post(
            "/api/v1/paiements",
            headers={"Authorization": f"Bearer {teacher_token}"},
            json={},
        )
    ).status_code == 403


@pytest.mark.asyncio
async def test_rbac_enseignant_interdit_comptabilite(client, teacher_token):
    assert (
        await client.get("/api/v1/comptabilite/depenses", headers={"Authorization": f"Bearer {teacher_token}"})
    ).status_code == 403


@pytest.mark.asyncio
async def test_rbac_enseignant_interdit_securite(client, teacher_token):
    assert (await client.get("/api/v1/securite/audit", headers={"Authorization": f"Bearer {teacher_token}"})).status_code == 403


@pytest.mark.asyncio
async def test_method_not_allowed_protegee(client, admin_token):
    r = await client.delete(
        "/api/v1/auth/login",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code in (405, 404)


@pytest.mark.asyncio
async def test_uuid_invalide_retourne_422(client, admin_token):
    r = await client.get(
        "/api/v1/eleves/not-a-uuid",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 422
