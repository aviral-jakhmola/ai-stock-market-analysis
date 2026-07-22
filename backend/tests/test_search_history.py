import pytest

pytestmark = pytest.mark.integration


def register_and_get_token(client, username, email, password="StrongPass123!"):
    client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestAuthRequired:
    def test_get_requires_auth(self, client):
        resp = client.get("/api/search-history")
        assert resp.status_code == 401

    def test_post_requires_auth(self, client):
        resp = client.post("/api/search-history", json={"ticker": "AAPL"})
        assert resp.status_code == 401


class TestLogSearch:
    def test_logging_creates_entry(self, authenticated_client):
        resp = authenticated_client.post("/api/search-history", json={"ticker": "AAPL"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["searched_at"] is not None

    def test_ticker_is_stored_as_sent_not_uppercased(self, authenticated_client):
        # Documenting current behavior: unlike watchlist, search history does NOT
        # normalize casing. "aapl" is stored as "aapl", not "AAPL".
        resp = authenticated_client.post("/api/search-history", json={"ticker": "aapl"})
        assert resp.json()["ticker"] == "aapl"

    def test_searching_same_ticker_again_does_not_duplicate(self, authenticated_client):
        authenticated_client.post("/api/search-history", json={"ticker": "AAPL"})
        authenticated_client.post("/api/search-history", json={"ticker": "AAPL"})

        history = authenticated_client.get("/api/search-history").json()
        assert len(history) == 1
        assert history[0]["ticker"] == "AAPL"

    def test_researching_ticker_updates_its_timestamp(self, authenticated_client):
        first = authenticated_client.post("/api/search-history", json={"ticker": "AAPL"}).json()
        authenticated_client.post("/api/search-history", json={"ticker": "TSLA"})
        second = authenticated_client.post("/api/search-history", json={"ticker": "AAPL"}).json()

        # Re-searching AAPL should bump its searched_at forward, not leave it at
        # the original timestamp from the first search.
        assert second["searched_at"] >= first["searched_at"]

        history = authenticated_client.get("/api/search-history").json()
        assert history[0]["ticker"] == "AAPL"  # most recently searched, back on top


class TestGetSearchHistory:
    def test_empty_history_returns_empty_list(self, authenticated_client):
        resp = authenticated_client.get("/api/search-history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_most_recent_search_first(self, authenticated_client):
        authenticated_client.post("/api/search-history", json={"ticker": "AAPL"})
        authenticated_client.post("/api/search-history", json={"ticker": "TSLA"})
        authenticated_client.post("/api/search-history", json={"ticker": "MSFT"})

        history = authenticated_client.get("/api/search-history").json()
        tickers = [item["ticker"] for item in history]
        assert tickers == ["MSFT", "TSLA", "AAPL"]

    def test_capped_at_10_most_recent(self, authenticated_client):
        tickers = [f"TICK{i}" for i in range(11)]  # 11 distinct tickers
        for t in tickers:
            authenticated_client.post("/api/search-history", json={"ticker": t})

        history = authenticated_client.get("/api/search-history").json()
        assert len(history) == 10

        returned_tickers = [item["ticker"] for item in history]
        assert "TICK0" not in returned_tickers  # oldest search, dropped
        assert "TICK10" in returned_tickers  # most recent, present
        assert returned_tickers[0] == "TICK10"  # most recent first

    def test_history_is_isolated_per_user(self, client):
        token_a = register_and_get_token(client, "histusera", "histusera@example.com")
        token_b = register_and_get_token(client, "histuserb", "histuserb@example.com")

        client.post("/api/search-history", json={"ticker": "AAPL"}, headers=auth_headers(token_a))
        client.post("/api/search-history", json={"ticker": "TSLA"}, headers=auth_headers(token_b))

        history_a = client.get("/api/search-history", headers=auth_headers(token_a)).json()
        history_b = client.get("/api/search-history", headers=auth_headers(token_b)).json()

        assert [i["ticker"] for i in history_a] == ["AAPL"]
        assert [i["ticker"] for i in history_b] == ["TSLA"]