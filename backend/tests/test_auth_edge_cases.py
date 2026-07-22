import pytest

pytestmark = pytest.mark.integration


class TestRegisterEdgeCases:
    def test_duplicate_username_returns_400(self, client, test_user_credentials):
        client.post("/api/auth/register", json=test_user_credentials)
        # Same username, different email
        dup = {**test_user_credentials, "email": "different@example.com"}
        resp = client.post("/api/auth/register", json=dup)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    def test_duplicate_email_returns_400(self, client, test_user_credentials):
        client.post("/api/auth/register", json=test_user_credentials)
        # Different username, same email
        dup = {**test_user_credentials, "username": "differentuser"}
        resp = client.post("/api/auth/register", json=dup)
        assert resp.status_code == 400

    def test_password_under_8_chars_rejected_by_validation(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "shortpw",
            "email": "shortpw@example.com",
            "password": "short",
        })
        # Pydantic field_validator raises before the route body even runs
        assert resp.status_code == 422

    def test_invalid_email_format_rejected(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "ValidPass123!",
        })
        assert resp.status_code == 422

    def test_response_never_includes_password_fields(self, client, test_user_credentials):
        resp = client.post("/api/auth/register", json=test_user_credentials)
        body = resp.json()
        assert "password" not in body
        assert "hashed_password" not in body


class TestLoginEdgeCases:
    def test_wrong_password_returns_401(self, client, test_user_credentials):
        client.post("/api/auth/register", json=test_user_credentials)
        resp = client.post("/api/auth/login", data={
            "username": test_user_credentials["username"],
            "password": "WrongPassword999!",
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Incorrect username or password"

    def test_nonexistent_username_returns_401(self, client):
        resp = client.post("/api/auth/login", data={
            "username": "ghost_user_never_registered",
            "password": "Whatever123!",
        })
        assert resp.status_code == 401

    def test_same_error_message_for_bad_username_vs_bad_password(self, client, test_user_credentials):
        # Security-relevant: the API shouldn't leak whether the username exists
        # by returning a different error for "wrong password" vs "no such user".
        client.post("/api/auth/register", json=test_user_credentials)

        wrong_password_resp = client.post("/api/auth/login", data={
            "username": test_user_credentials["username"],
            "password": "WrongPass999!",
        })
        wrong_username_resp = client.post("/api/auth/login", data={
            "username": "totally_different_user",
            "password": "WrongPass999!",
        })
        assert wrong_password_resp.json()["detail"] == wrong_username_resp.json()["detail"]


class TestProtectedRouteEdgeCases:
    def test_me_without_token_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_with_malformed_token_returns_401(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-jwt"})
        assert resp.status_code == 401

    def test_me_with_wrong_scheme_returns_401(self, client, authenticated_client):
        # authenticated_client already has a valid token; grab it and resend
        # with the wrong auth scheme ("Token" instead of "Bearer").
        token = authenticated_client.headers["Authorization"].split(" ")[1]
        resp = client.get("/api/auth/me", headers={"Authorization": f"Token {token}"})
        assert resp.status_code == 401

    def test_me_with_token_for_deleted_user_returns_401(self, client, db_session, test_user_credentials):
        from app.models.user import User

        client.post("/api/auth/register", json=test_user_credentials)
        login_resp = client.post("/api/auth/login", data={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"],
        })
        token = login_resp.json()["access_token"]

        # Delete the user directly via the DB session, simulating an account
        # removed after the token was issued.
        user = db_session.query(User).filter(User.username == test_user_credentials["username"]).first()
        db_session.delete(user)
        db_session.commit()

        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        