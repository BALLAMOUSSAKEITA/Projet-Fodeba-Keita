from datetime import date

import pytest


async def _setup_eleve(client, admin_token):
    classes = (await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    annee = (await client.get(
        "/api/v1/parametrage/annees-scolaires/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    types_frais = (await client.get(
        "/api/v1/parametrage/types-frais",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()
    classe = classes[0]
    scolarite = next(tf for tf in types_frais if tf["code"] == "SCOLARITE")

    eleve = (await client.post(
        "/api/v1/eleves",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "PayTest",
            "prenoms": "Eleve",
            "sexe": "M",
            "date_naissance": "2015-03-01",
            "niveau_id": classe["niveau_id"],
            "tuteurs": [{"type": "pere", "nom": "T", "prenoms": "P", "telephone": "+224621000077"}],
        },
    )).json()

    await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"classe_id": classe["id"]},
    )
    return eleve, annee, scolarite, classe


@pytest.mark.asyncio
async def test_tarifs_et_tranches(client, admin_token):
    annee = (await client.get(
        "/api/v1/parametrage/annees-scolaires/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()

    r = await client.get(
        f"/api/v1/paiements/tarifs?annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 9

    r2 = await client.get(
        f"/api/v1/paiements/tranches?annee_scolaire_id={annee['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r2.status_code == 200
    assert len(r2.json()) >= 3


@pytest.mark.asyncio
async def test_encaissement_et_situation(client, admin_token):
    eleve, annee, scolarite, _ = await _setup_eleve(client, admin_token)
    tranches = (await client.get(
        f"/api/v1/paiements/tranches?annee_scolaire_id={annee['id']}&type_frais_id={scolarite['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )).json()

    r = await client.post(
        "/api/v1/paiements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "type_frais_id": scolarite["id"],
            "tranche_id": tranches[0]["id"],
            "montant": 800000,
            "mode_paiement": "especes",
            "date_paiement": date.today().isoformat(),
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["numero_recu"].startswith("REC-")
    assert data["statut"] == "valide"

    sit = await client.get(
        f"/api/v1/paiements/eleve/{eleve['id']}/situation",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert sit.status_code == 200
    assert float(sit.json()["total_paye"]) >= 800000


@pytest.mark.asyncio
async def test_recu_pdf(client, admin_token):
    eleve, annee, scolarite, _ = await _setup_eleve(client, admin_token)

    pay = (await client.post(
        "/api/v1/paiements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "type_frais_id": scolarite["id"],
            "montant": 300000,
            "mode_paiement": "orange_money",
            "reference_externe": "OM123456",
        },
    )).json()

    r = await client.get(
        f"/api/v1/paiements/{pay['id']}/recu/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 500


@pytest.mark.asyncio
async def test_impayes_et_caisse(client, admin_token):
    eleve, annee, scolarite, classe = await _setup_eleve(client, admin_token)
    today = date.today().isoformat()

    await client.post(
        "/api/v1/paiements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "type_frais_id": scolarite["id"],
            "montant": 100000,
            "mode_paiement": "especes",
        },
    )

    imp = await client.get(
        f"/api/v1/paiements/impayes/liste?classe_id={classe['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert imp.status_code == 200
    assert isinstance(imp.json(), list)

    caisse = await client.get(
        f"/api/v1/paiements/caisse/journaliere?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert caisse.status_code == 200
    assert caisse.json()["nombre_paiements"] >= 1


@pytest.mark.asyncio
async def test_annulation_et_remise(client, admin_token):
    eleve, annee, scolarite, _ = await _setup_eleve(client, admin_token)

    pay = (await client.post(
        "/api/v1/paiements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "type_frais_id": scolarite["id"],
            "montant": 50000,
            "mode_paiement": "especes",
        },
    )).json()

    r = await client.post(
        f"/api/v1/paiements/{pay['id']}/annuler",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"motif": "Erreur de saisie"},
    )
    assert r.status_code == 200
    assert r.json()["statut"] == "annule"

    r2 = await client.post(
        "/api/v1/paiements/remises",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "eleve_id": eleve["id"],
            "annee_scolaire_id": annee["id"],
            "type_frais_id": scolarite["id"],
            "montant": 100000,
            "motif": "Bourse sociale",
        },
    )
    assert r2.status_code == 201
