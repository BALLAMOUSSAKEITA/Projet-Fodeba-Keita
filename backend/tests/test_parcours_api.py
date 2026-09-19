"""
Parcours API complet — inscription → notes → bulletin → paiement.
Équivalent E2E backend du critère de recette Sprint 19.
"""

import pytest


@pytest.mark.asyncio
async def test_parcours_inscription_bulletin_paiement(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    classes = (await client.get("/api/v1/parametrage/classes", headers=headers)).json()
    classe = classes[0]
    matieres = (await client.get("/api/v1/parametrage/matieres", headers=headers)).json()
    annee = (await client.get("/api/v1/parametrage/annees-scolaires/active", headers=headers)).json()
    periodes = (
        await client.get(f"/api/v1/parametrage/periodes?annee_scolaire_id={annee['id']}", headers=headers)
    ).json()
    types_eval = (await client.get("/api/v1/notes/types-evaluation", headers=headers)).json()
    types_frais = (await client.get("/api/v1/parametrage/types-frais", headers=headers)).json()
    scol = next(t for t in types_frais if t["code"] == "SCOLARITE")

    # 1. Inscription élève
    eleve = (
        await client.post(
            "/api/v1/eleves",
            headers=headers,
            json={
                "nom": "Parcours",
                "prenoms": "Complet",
                "sexe": "F",
                "date_naissance": "2015-08-15",
                "niveau_id": classe["niveau_id"],
                "tuteurs": [
                    {"type": "mere", "nom": "Parcours", "prenoms": "Maman", "telephone": "+224621777777"}
                ],
            },
        )
    ).json()
    assert eleve["matricule"]

    # 2. Affectation classe
    aff = await client.post(
        f"/api/v1/eleves/{eleve['id']}/affecter-classe",
        headers=headers,
        json={"classe_id": classe["id"]},
    )
    assert aff.status_code == 200

    dossier = (await client.get(f"/api/v1/eleves/{eleve['id']}", headers=headers)).json()
    assert dossier["inscriptions"]

    # 3. Saisie notes
    evaluation = (
        await client.post(
            "/api/v1/notes/evaluations",
            headers=headers,
            json={
                "libelle": "Parcours T1",
                "classe_id": classe["id"],
                "matiere_id": matieres[0]["id"],
                "periode_id": periodes[0]["id"],
                "type_evaluation_id": types_eval[0]["id"],
            },
        )
    ).json()
    notes = await client.put(
        f"/api/v1/notes/evaluations/{evaluation['id']}/notes",
        headers=headers,
        json={"notes": [{"eleve_id": eleve["id"], "valeur": 15, "is_absent": False}]},
    )
    assert notes.status_code == 200

    moyennes = await client.get(
        f"/api/v1/notes/classes/{classe['id']}/periodes/{periodes[0]['id']}/moyennes",
        headers=headers,
    )
    assert moyennes.status_code == 200

    # 4. Bulletin
    bulletin = await client.get(
        f"/api/v1/bulletins/eleve/{eleve['id']}/periodes/{periodes[0]['id']}/pdf",
        headers=headers,
    )
    assert bulletin.status_code == 200
    assert bulletin.headers["content-type"] == "application/pdf"

    stats = await client.get(
        f"/api/v1/bulletins/classes/{classe['id']}/periodes/{periodes[0]['id']}/stats",
        headers=headers,
    )
    assert stats.status_code == 200

    # 5. Paiement et solde
    paiement = (
        await client.post(
            "/api/v1/paiements",
            headers=headers,
            json={
                "eleve_id": eleve["id"],
                "type_frais_id": scol["id"],
                "montant": 75000,
                "mode_paiement": "especes",
                "annee_scolaire_id": annee["id"],
            },
        )
    ).json()
    assert paiement["numero_recu"]

    recu = await client.get(f"/api/v1/paiements/{paiement['id']}/recu/pdf", headers=headers)
    assert recu.status_code == 200

    situation = (
        await client.get(f"/api/v1/paiements/eleve/{eleve['id']}/situation", headers=headers)
    ).json()
    assert situation["eleve_id"] == eleve["id"]
    assert float(situation["total_paye"]) >= 75000
