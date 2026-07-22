def test_root_route_works(client):
    """If this fails, the TestClient/app wiring itself is broken."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to AI Stock Market API"}


def test_register_and_login_flow(client, test_user_credentials):
    """If this fails, register/login payload shapes are wrong."""
    register_resp = client.post("/api/auth/register", json=test_user_credentials)
    assert register_resp.status_code == 200
    assert register_resp.json()["username"] == test_user_credentials["username"]

    login_resp = client.post(
        "/api/auth/login",
        data={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"],
        },
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_authenticated_client_hits_protected_route(authenticated_client, test_user_credentials):
    """If this fails, the auth override/fixture chain is broken."""
    resp = authenticated_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == test_user_credentials["username"]