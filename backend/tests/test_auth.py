import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fodebakeita.gn", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "super_admin"
    assert "users.manage" in data["user"]["permissions"]


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fodebakeita.gn", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_account_lockout_after_failed_attempts(client):
    for _ in range(5):
        await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@fodebakeita.gn", "password": "wrong"},
        )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fodebakeita.gn", "password": "admin123"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me(client, admin_token):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@fodebakeita.gn"


@pytest.mark.asyncio
async def test_rbac_forbidden_for_teacher(client, teacher_token):
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_as_admin(client, admin_token):
    roles_response = await client.get(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    parent_role = next(r for r in roles_response.json() if r["code"] == "parent")

    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "parent.test@fodebakeita.gn",
            "password": "parent1234",
            "nom": "Test",
            "prenom": "Parent",
            "telephone": "+224620000099",
            "role_id": parent_role["id"],
            "is_active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "parent.test@fodebakeita.gn"


@pytest.mark.asyncio
async def test_password_reset_flow(client, admin_token):
    forgot = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "directeur@fodebakeita.gn"},
    )
    assert forgot.status_code == 200
    token = forgot.json()["reset_token"]
    assert token

    reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "newdirecteur123"},
    )
    assert reset.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "directeur@fodebakeita.gn", "password": "newdirecteur123"},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token(client):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fodebakeita.gn", "password": "admin123"},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_list_roles(client, admin_token):
    response = await client.get(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 7
