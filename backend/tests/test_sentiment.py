import pytest

from app.services.sentiment import analyze_sentiment, analyze_ticker_sentiment


class TestAnalyzeSentiment:
    # Marked slow: these call the real FinBERT pipeline (already loaded at
    # module import time). Skip with `pytest -m "not slow"` for a fast run.

    @pytest.mark.slow
    def test_clearly_positive_headline(self):
        result = analyze_sentiment("Company reports record profits and raises full-year guidance.")
        assert result["label"] == "positive"
        assert 0.0 <= result["score"] <= 1.0

    @pytest.mark.slow
    def test_clearly_negative_headline(self):
        result = analyze_sentiment("Company issues profit warning after massive losses and mass layoffs.")
        assert result["label"] == "negative"
        assert 0.0 <= result["score"] <= 1.0


class TestAnalyzeTickerSentimentAggregation:
    # These mock fetch_news AND analyze_sentiment, so no real model inference
    # happens here -- these test the counting/aggregation logic in isolation.

    @pytest.mark.unit
    def test_no_articles_returns_neutral_default(self, monkeypatch):
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: [])
        result = analyze_ticker_sentiment("FAKE.NS")
        assert result == {
            "ticker": "FAKE.NS",
            "articles": [],
            "summary": {"positive": 0, "negative": 0, "neutral": 0},
            "overall_sentiment": "neutral",
        }

    @pytest.mark.unit
    def test_aggregates_counts_and_picks_majority_label(self, monkeypatch):
        fake_articles = [{"title": "A", "url": "u1"}, {"title": "B", "url": "u2"}, {"title": "C", "url": "u3"}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)

        labels = iter(["positive", "positive", "negative"])
        monkeypatch.setattr(
            "app.services.sentiment.analyze_sentiment",
            lambda text: {"label": next(labels), "score": 0.9},
        )

        result = analyze_ticker_sentiment("FAKE.NS", limit=3)
        assert result["summary"] == {"positive": 2, "negative": 1, "neutral": 0}
        assert result["overall_sentiment"] == "positive"
        assert len(result["articles"]) == 3
        assert result["articles"][0]["title"] == "A"  # original article fields preserved
        assert result["articles"][0]["sentiment"]["label"] == "positive"

    @pytest.mark.unit
    def test_articles_without_a_title_are_skipped(self, monkeypatch):
        fake_articles = [{"title": "Real headline"}, {"title": None}, {"title": ""}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)
        monkeypatch.setattr("app.services.sentiment.analyze_sentiment", lambda text: {"label": "neutral", "score": 0.5})

        result = analyze_ticker_sentiment("FAKE.NS")
        assert len(result["articles"]) == 1
        assert result["summary"] == {"positive": 0, "negative": 0, "neutral": 1}

    @pytest.mark.unit
    def test_tie_break_order_documents_current_behavior(self, monkeypatch):
        # counts dict is built as {"positive": 0, "negative": 0, "neutral": 0}.
        # On a tie, max(counts, key=counts.get) returns the first key hit during
        # iteration with the max value -- so "positive" wins ties over "negative".
        # Documenting this rather than asserting it's the "right" choice.
        fake_articles = [{"title": "A"}, {"title": "B"}]
        monkeypatch.setattr("app.services.sentiment.fetch_news", lambda ticker, limit=10: fake_articles)
        labels = iter(["positive", "negative"])
        monkeypatch.setattr(
            "app.services.sentiment.analyze_sentiment",
            lambda text: {"label": next(labels), "score": 0.5},
        )
        result = analyze_ticker_sentiment("FAKE.NS")
        assert result["summary"] == {"positive": 1, "negative": 1, "neutral": 0}
        assert result["overall_sentiment"] == "positive"