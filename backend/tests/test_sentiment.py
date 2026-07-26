import pytest

from app.services.sentiment import analyze_sentiment, analyze_ticker_sentiment


class TestAnalyzeSentiment:
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_clearly_positive_headline(self):
        result = await analyze_sentiment("Company reports record profits and raises full-year guidance.")
        assert result["label"] == "positive"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_clearly_negative_headline(self):
        result = await analyze_sentiment("Company issues profit warning after massive losses and mass layoffs.")
        assert result["label"] == "negative"


class TestAnalyzeTickerSentimentAggregation:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_articles_returns_neutral_default(self, monkeypatch):
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: [])
        result = await analyze_ticker_sentiment("FAKE.NS")
        assert result == {
            "ticker": "FAKE.NS",
            "articles": [],
            "summary": {"positive": 0, "negative": 0, "neutral": 0},
            "overall_sentiment": "neutral",
        }

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_aggregates_counts_and_picks_majority_label(self, monkeypatch):
        fake_articles = [{"title": "A", "url": "u1"}, {"title": "B", "url": "u2"}, {"title": "C", "url": "u3"}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)

        labels = iter(["positive", "positive", "negative"])

        async def fake_analyze_sentiment(text):
            return {"label": next(labels), "score": 0.9}

        monkeypatch.setattr("app.services.sentiment.analyze_sentiment", fake_analyze_sentiment)

        result = await analyze_ticker_sentiment("FAKE.NS", limit=3)
        assert result["summary"] == {"positive": 2, "negative": 1, "neutral": 0}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_articles_without_a_title_are_skipped(self, monkeypatch):
        fake_articles = [{"title": "Real headline"}, {"title": None}, {"title": ""}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)

        async def fake_analyze_sentiment(text):
            return {"label": "neutral", "score": 0.5}

        monkeypatch.setattr("app.services.sentiment.analyze_sentiment", fake_analyze_sentiment)

        result = await analyze_ticker_sentiment("FAKE.NS")
        assert len(result["articles"]) == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_tie_break_order_documents_current_behavior(self, monkeypatch):
        fake_articles = [{"title": "A"}, {"title": "B"}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)
        labels = iter(["positive", "negative"])

        async def fake_analyze_sentiment(text):
            return {"label": next(labels), "score": 0.5}

        monkeypatch.setattr("app.services.sentiment.analyze_sentiment", fake_analyze_sentiment)

        result = await analyze_ticker_sentiment("FAKE.NS")
        assert result["summary"] == {"positive": 1, "negative": 1, "neutral": 0}