import pytest


@pytest.mark.asyncio
async def test_audit_et_sauvegarde(client, admin_token):
    r = await client.get(
        "/api/v1/securite/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r2 = await client.get(
        "/api/v1/securite/sauvegarde",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert "procedure_restauration" in r2.json()


@pytest.mark.asyncio
async def test_historique_paiement_apres_encaissement(client, admin_token):
    annee = (
        await client.get(
            "/api/v1/parametrage/annees-scolaires/active",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    niveau = next(
        n for n in (
            await client.get("/api/v1/parametrage/niveaux", headers={"Authorization": f"Bearer {admin_token}"})
        ).json()
        if n["code"] == "3A"
    )
    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Audit",
                "prenoms": "Test Paiement",
                "sexe": "M",
                "date_naissance": "2015-05-01",
                "niveau_id": niveau["id"],
                "tuteurs": [{"type": "pere", "nom": "Audit", "prenoms": "Papa", "telephone": "+224621234567"}],
            },
        )
    ).json()
    types_frais = (
        await client.get("/api/v1/parametrage/types-frais", headers={"Authorization": f"Bearer {admin_token}"})
    ).json()
    scol = next(t for t in types_frais if t["code"] == "SCOLARITE")

    paiement = (
        await client.post(
            "/api/v1/paiements",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "eleve_id": eleve["id"],
                "type_frais_id": scol["id"],
                "montant": 50000,
                "mode_paiement": "especes",
                "annee_scolaire_id": annee["id"],
            },
        )
    ).json()

    hist = await client.get(
        f"/api/v1/securite/historique/paiements?eleve_id={eleve['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert hist.status_code == 200
    assert len(hist.json()) >= 1
    assert hist.json()[0]["action"] == "create"

    audit = await client.get(
        "/api/v1/securite/audit?resource_type=paiement",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert audit.status_code == 200
    assert any(a["resource_id"] == paiement["id"] for a in audit.json())


@pytest.mark.asyncio
async def test_cloture_annee(client, admin_token):
    created = await client.post(
        "/api/v1/parametrage/annees-scolaires",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"libelle": "2023-2024", "date_debut": "2023-09-01", "date_fin": "2024-06-30"},
    )
    assert created.status_code == 201
    annee_id = created.json()["id"]

    r = await client.post(
        f"/api/v1/securite/annees/{annee_id}/cloturer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["statut"] == "cloturee"

    audit = await client.get(
        "/api/v1/securite/audit?action=cloture",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert any(a["resource_id"] == annee_id for a in audit.json())


@pytest.mark.asyncio
async def test_annee_cloturee_bloque_paiement(client, admin_token):
    created = await client.post(
        "/api/v1/parametrage/annees-scolaires",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"libelle": "2022-2023", "date_debut": "2022-09-01", "date_fin": "2023-06-30"},
    )
    annee_id = created.json()["id"]
    await client.post(
        f"/api/v1/securite/annees/{created.json()['id']}/cloturer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    niveau = next(
        n for n in (
            await client.get("/api/v1/parametrage/niveaux", headers={"Authorization": f"Bearer {admin_token}"})
        ).json()
        if n["code"] == "3A"
    )
    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nom": "Bloque",
                "prenoms": "Cloture",
                "sexe": "M",
                "date_naissance": "2015-01-01",
                "niveau_id": niveau["id"],
                "tuteurs": [{"type": "pere", "nom": "B", "prenoms": "P", "telephone": "+224621234568"}],
            },
        )
    ).json()
    types_frais = (
        await client.get("/api/v1/parametrage/types-frais", headers={"Authorization": f"Bearer {admin_token}"})
    ).json()
    scol = next(t for t in types_frais if t["code"] == "SCOLARITE")

    r = await client.post(
        "/api/v1/paiements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "type_frais_id": scol["id"],
            "montant": 10000,
            "mode_paiement": "especes",
            "annee_scolaire_id": annee_id,
        },
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_securite_permission_refusee(client, teacher_token):
    r = await client.get(
        "/api/v1/securite/audit",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r.status_code == 403
