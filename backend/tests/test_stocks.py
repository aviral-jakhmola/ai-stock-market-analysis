import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.integration


def make_synthetic_history_df(n=100, seed=7):
    """OHLCV + date, enough rows for all indicators to have real (non-NaN) values."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    steps = rng.normal(loc=0.05, scale=1.0, size=n)
    close = 100 + np.cumsum(steps)
    open_ = close - rng.normal(0, 0.3, size=n)
    high = np.maximum(open_, close) + rng.uniform(0, 0.5, size=n)
    low = np.minimum(open_, close) - rng.uniform(0, 0.5, size=n)
    volume = rng.integers(1_000_000, 5_000_000, size=n)
    return pd.DataFrame({
        "date": dates, "open": open_, "high": high, "low": low,
        "close": close, "volume": volume,
    })


class TestSearchEndpoint:
    # Pure/no mocking needed — searches a hardcoded in-memory list.

    def test_search_matches_partial_ticker(self, client):
        resp = client.get("/api/stocks/search", params={"q": "AAPL"})
        assert resp.status_code == 200
        assert "AAPL" in resp.json()["results"]

    def test_search_is_case_insensitive(self, client):
        resp = client.get("/api/stocks/search", params={"q": "aapl"})
        assert "AAPL" in resp.json()["results"]

    def test_search_no_match_returns_empty_list(self, client):
        resp = client.get("/api/stocks/search", params={"q": "ZZZZZ_NOT_REAL"})
        assert resp.json()["results"] == []

    def test_search_partial_ns_suffix_matches_indian_stocks(self, client):
        resp = client.get("/api/stocks/search", params={"q": "RELIANCE"})
        assert "RELIANCE.NS" in resp.json()["results"]


class TestCompanyOverview:
    def test_returns_company_data(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.routers.stocks.fetch_company_overview",
            lambda symbol: {
                "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics",
                "market_cap": 3.0e12, "pe_ratio": 30.5, "eps": 6.1,
                "fifty_two_week_high": 200.0, "fifty_two_week_low": 150.0,
                "dividend_yield": 0.005, "beta": 1.2, "currency": "USD",
            },
        )
        resp = client.get("/api/stocks/company/AAPL")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Apple Inc."

    def test_unknown_symbol_returns_404(self, monkeypatch, client):
        def raise_value_error(symbol):
            raise ValueError(f"No data found for {symbol}")
        monkeypatch.setattr("app.routers.stocks.fetch_company_overview", raise_value_error)

        resp = client.get("/api/stocks/company/FAKE123")
        assert resp.status_code == 404


class TestHistoryEndpoint:
    def test_returns_history_with_indicators(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.fetch_stock_data",
            lambda ticker, period: make_synthetic_history_df(),
        )
        resp = client.get("/api/stocks/AAPL/history", params={"timeframe": "1Y"})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 100
        last_row = body[-1]
        # After 100 rows, warmup periods (max 50 for sma_50/ema_50) are long past.
        assert last_row["sma_20"] is not None
        assert last_row["rsi_14"] is not None

    def test_invalid_timeframe_returns_400(self, client):
        resp = client.get("/api/stocks/AAPL/history", params={"timeframe": "3Y"})
        assert resp.status_code == 400
        assert "Invalid timeframe" in resp.json()["detail"]

    def test_unknown_ticker_returns_404(self, monkeypatch, client):
        def raise_value_error(ticker, period):
            raise ValueError(f"No data found for {ticker}")
        monkeypatch.setattr("app.routers.stocks.fetch_stock_data", raise_value_error)

        resp = client.get("/api/stocks/FAKE123/history")
        assert resp.status_code == 404

    def test_unexpected_error_returns_500(self, monkeypatch, client):
        def raise_generic_error(ticker, period):
            raise RuntimeError("yfinance timed out")
        monkeypatch.setattr("app.routers.stocks.fetch_stock_data", raise_generic_error)

        resp = client.get("/api/stocks/AAPL/history")
        assert resp.status_code == 500


class TestRecommendationEndpoint:
    def test_returns_well_formed_recommendation(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.fetch_stock_data",
            lambda ticker, period: make_synthetic_history_df(),
        )
        resp = client.get("/api/stocks/AAPL/recommendation")
        assert resp.status_code == 200
        body = resp.json()
        assert body["recommendation"] in {"BUY", "SELL", "HOLD"}
        assert "votes" in body
        assert "historical_accuracy" in body

    def test_invalid_timeframe_returns_400(self, client):
        resp = client.get("/api/stocks/AAPL/recommendation", params={"timeframe": "10Y"})
        assert resp.status_code == 400


class TestSentimentEndpoint:
    def test_returns_mocked_sentiment(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.analyze_ticker_sentiment",
            lambda ticker, limit=10: {
                "ticker": ticker,
                "articles": [
                    {"title": "Good news", "publisher": "Reuters", "link": "http://x",
                     "published": "2024-01-01", "sentiment": {"label": "positive", "score": 0.9}},
                ],
                "summary": {"positive": 1, "negative": 0, "neutral": 0},
                "overall_sentiment": "positive",
            },
        )
        resp = client.get("/api/stocks/AAPL/sentiment")
        assert resp.status_code == 200
        assert resp.json()["overall_sentiment"] == "positive"

    def test_error_returns_500(self, monkeypatch, client):
        def raise_error(ticker, limit=10):
            raise RuntimeError("FinBERT model error")
        monkeypatch.setattr("app.routers.stocks.analyze_ticker_sentiment", raise_error)

        resp = client.get("/api/stocks/AAPL/sentiment")
        assert resp.status_code == 500


class TestPredictEndpoint:
    def test_returns_mocked_prediction(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.predict_direction",
            lambda ticker: {
                "ticker": ticker, "direction": "UP",
                "probability_up": 0.55, "probability_down": 0.45,
                "model_accuracy_on_test_set": 0.508,
            },
        )
        resp = client.get("/api/stocks/AAPL/predict")
        assert resp.status_code == 200
        assert resp.json()["direction"] == "UP"

    def test_error_returns_500(self, monkeypatch, client):
        def raise_error(ticker):
            raise RuntimeError("XGBoost training failed")
        monkeypatch.setattr("app.routers.stocks.predict_direction", raise_error)

        resp = client.get("/api/stocks/AAPL/predict")
        assert resp.status_code == 500


class TestFinalRecommendationEndpoint:
    def test_returns_mocked_final_recommendation(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.get_final_recommendation",
            lambda ticker, timeframe="1Y": {
                "ticker": ticker,
                "final_recommendation": "BUY",
                "note": "All three signals agree (bullish).",
                "breakdown": {
                    "technical": {"vote": "bullish", "weight": 3, "detail": "BUY", "backtested": {"success_rate_pct": 61.5}},
                    "ml": {"vote": "bullish", "weight": 1, "detail": "UP", "model_accuracy": 0.51},
                    "sentiment": {"vote": "bullish", "weight": 1, "detail": "positive"},
                },
                "weighted_bullish": 5,
                "weighted_bearish": 0,
                "total_weight": 5,
            },
        )
        resp = client.get("/api/stocks/AAPL/final-recommendation")
        assert resp.status_code == 200
        body = resp.json()
        assert body["final_recommendation"] == "BUY"
        assert body["total_weight"] == 5

    def test_error_returns_500(self, monkeypatch, client):
        def raise_error(ticker, timeframe="1Y"):
            raise RuntimeError("ensemble pipeline failed")
        monkeypatch.setattr("app.routers.stocks.get_final_recommendation", raise_error)

        resp = client.get("/api/stocks/AAPL/final-recommendation")
        assert resp.status_code == 500

class TestRecommendationEndpoint:
    def test_returns_well_formed_recommendation(self, monkeypatch, client):
        monkeypatch.setattr(
            "app.routers.stocks.fetch_stock_data",
            lambda ticker, period: make_synthetic_history_df(),
        )
        resp = client.get("/api/stocks/AAPL/recommendation")
        assert resp.status_code == 200
        body = resp.json()
        assert body["recommendation"] in {"BUY", "SELL", "HOLD"}
        assert "votes" in body
        assert "historical_accuracy" in body

    def test_invalid_timeframe_returns_400(self, client):
        resp = client.get("/api/stocks/AAPL/recommendation", params={"timeframe": "10Y"})
        assert resp.status_code == 400

    def test_unknown_ticker_returns_404(self, monkeypatch, client):
        def raise_value_error(ticker, period):
            raise ValueError(f"No data found for {ticker}")
        monkeypatch.setattr("app.routers.stocks.fetch_stock_data", raise_value_error)

        resp = client.get("/api/stocks/FAKE123/recommendation")
        assert resp.status_code == 404

    def test_unexpected_error_returns_500(self, monkeypatch, client):
        def raise_generic_error(ticker, period):
            raise RuntimeError("yfinance timed out")
        monkeypatch.setattr("app.routers.stocks.fetch_stock_data", raise_generic_error)

        resp = client.get("/api/stocks/AAPL/recommendation")
        assert resp.status_code == 500
        