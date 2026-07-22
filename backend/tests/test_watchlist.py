import pytest

pytestmark = pytest.mark.integration


def register_and_get_token(client, username, email, password="StrongPass123!"):
    client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestAuthRequired:
    def test_get_watchlist_requires_auth(self, client):
        resp = client.get("/api/watchlist")
        assert resp.status_code == 401

    def test_post_watchlist_requires_auth(self, client):
        resp = client.post("/api/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 401

    def test_delete_watchlist_requires_auth(self, client):
        resp = client.delete("/api/watchlist/1")
        assert resp.status_code == 401


class TestGetWatchlist:
    def test_empty_watchlist_returns_empty_list(self, authenticated_client):
        resp = authenticated_client.get("/api/watchlist")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_added_items(self, authenticated_client):
        authenticated_client.post("/api/watchlist", json={"ticker": "AAPL"})
        authenticated_client.post("/api/watchlist", json={"ticker": "TSLA"})
        resp = authenticated_client.get("/api/watchlist")
        tickers = {item["ticker"] for item in resp.json()}
        assert tickers == {"AAPL", "TSLA"}


class TestAddToWatchlist:
    def test_ticker_is_uppercased(self, authenticated_client):
        resp = authenticated_client.post("/api/watchlist", json={"ticker": "aapl"})
        assert resp.status_code == 200
        assert resp.json()["ticker"] == "AAPL"

    def test_response_includes_id_and_added_at(self, authenticated_client):
        resp = authenticated_client.post("/api/watchlist", json={"ticker": "MSFT"})
        body = resp.json()
        assert isinstance(body["id"], int)
        assert body["added_at"] is not None

    def test_duplicate_ticker_returns_400(self, authenticated_client):
        authenticated_client.post("/api/watchlist", json={"ticker": "AAPL"})
        resp = authenticated_client.post("/api/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 400
        assert "already in your watchlist" in resp.json()["detail"]

    def test_duplicate_check_is_case_insensitive_via_uppercasing(self, authenticated_client):
        # "aapl" and "AAPL" both normalize to "AAPL" before hitting the unique constraint.
        authenticated_client.post("/api/watchlist", json={"ticker": "aapl"})
        resp = authenticated_client.post("/api/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 400


class TestRemoveFromWatchlist:
    def test_removes_own_item(self, authenticated_client):
        add_resp = authenticated_client.post("/api/watchlist", json={"ticker": "NFLX"})
        item_id = add_resp.json()["id"]

        del_resp = authenticated_client.delete(f"/api/watchlist/{item_id}")
        assert del_resp.status_code == 200

        get_resp = authenticated_client.get("/api/watchlist")
        assert get_resp.json() == []

    def test_removing_nonexistent_item_returns_404(self, authenticated_client):
        resp = authenticated_client.delete("/api/watchlist/99999")
        assert resp.status_code == 404

    def test_cannot_remove_another_users_item(self, client):
        token_a = register_and_get_token(client, "usera", "usera@example.com")
        add_resp = client.post(
            "/api/watchlist", json={"ticker": "GOOGL"}, headers=auth_headers(token_a)
        )
        item_id = add_resp.json()["id"]

        token_b = register_and_get_token(client, "userb", "userb@example.com")
        del_resp = client.delete(f"/api/watchlist/{item_id}", headers=auth_headers(token_b))
        assert del_resp.status_code == 404

        # Confirm it's still there for user A
        get_resp = client.get("/api/watchlist", headers=auth_headers(token_a))
        assert len(get_resp.json()) == 1

    def test_watchlists_are_isolated_per_user(self, client):
        token_a = register_and_get_token(client, "usera2", "usera2@example.com")
        token_b = register_and_get_token(client, "userb2", "userb2@example.com")

        client.post("/api/watchlist", json={"ticker": "AAPL"}, headers=auth_headers(token_a))
        client.post("/api/watchlist", json={"ticker": "TSLA"}, headers=auth_headers(token_b))

        list_a = client.get("/api/watchlist", headers=auth_headers(token_a)).json()
        list_b = client.get("/api/watchlist", headers=auth_headers(token_b)).json()

        assert [i["ticker"] for i in list_a] == ["AAPL"]
        assert [i["ticker"] for i in list_b] == ["TSLA"]

class TestWatchlistOrdering:
    def test_most_recently_added_appears_first(self, authenticated_client):
        authenticated_client.post("/api/watchlist", json={"ticker": "AAPL"})
        authenticated_client.post("/api/watchlist", json={"ticker": "TSLA"})
        authenticated_client.post("/api/watchlist", json={"ticker": "MSFT"})

        resp = authenticated_client.get("/api/watchlist")
        tickers = [item["ticker"] for item in resp.json()]
        assert tickers == ["MSFT", "TSLA", "AAPL"]