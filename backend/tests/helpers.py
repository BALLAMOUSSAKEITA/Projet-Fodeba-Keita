async def get_niveau_by_code(client, token: str, code: str = "3A"):
    response = await client.get(
        "/api/v1/parametrage/niveaux",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return next(n for n in response.json() if n["code"] == code)


async def get_classe_for_niveau(client, token: str, niveau_id: str):
    response = await client.get(
        "/api/v1/parametrage/classes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return next(c for c in response.json() if c["niveau_id"] == niveau_id)


async def default_eleve_create_payload(client, token: str, niveau_code: str = "3A", **overrides):
    niveau = await get_niveau_by_code(client, token, niveau_code)
    classe = await get_classe_for_niveau(client, token, niveau["id"])
    payload = {
        "nom": "Test",
        "prenoms": "Eleve",
        "sexe": "M",
        "date_naissance": "2015-01-01",
        "niveau_id": niveau["id"],
        "classe_id": classe["id"],
        "tuteurs": [{"type": "pere", "nom": "T", "prenoms": "P", "telephone": "+224621000000"}],
    }
    payload.update(overrides)
    return payload
