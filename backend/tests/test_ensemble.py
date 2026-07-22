import pytest
import pandas as pd

from app.services.ensemble import (
    combine_signals,
    _technical_vote,
    _ml_vote,
    _sentiment_vote,
)

pytestmark = pytest.mark.unit


class TestVoteMapping:
    @pytest.mark.parametrize("rec,expected", [
        ("BUY", "bullish"),
        ("SELL", "bearish"),
        ("HOLD", "neutral"),
    ])
    def test_technical_vote(self, rec, expected):
        assert _technical_vote({"recommendation": rec}) == expected

    @pytest.mark.parametrize("direction,expected", [
        ("UP", "bullish"),
        ("DOWN", "bearish"),
    ])
    def test_ml_vote(self, direction, expected):
        assert _ml_vote({"direction": direction}) == expected

    @pytest.mark.parametrize("overall,expected", [
        ("positive", "bullish"),
        ("negative", "bearish"),
        ("neutral", "neutral"),
    ])
    def test_sentiment_vote(self, overall, expected):
        assert _sentiment_vote({"overall_sentiment": overall}) == expected


class TestCombineSignals:
    def test_all_bullish_is_buy(self):
        result = combine_signals(
            technical={"recommendation": "BUY"},
            prediction={"direction": "UP"},
            sentiment={"overall_sentiment": "positive"},
        )
        assert result["final_recommendation"] == "BUY"
        assert "All three signals agree" in result["note"]
        assert result["weighted_bullish"] == 5
        assert result["weighted_bearish"] == 0

    def test_all_bearish_is_sell(self):
        result = combine_signals(
            technical={"recommendation": "SELL"},
            prediction={"direction": "DOWN"},
            sentiment={"overall_sentiment": "negative"},
        )
        assert result["final_recommendation"] == "SELL"
        assert "All three signals agree" in result["note"]

    def test_technical_outweighs_single_opposing_signal(self):
        # technical(BUY, weight 3) vs ml(DOWN, weight 1); sentiment neutral
        # bullish=3, bearish=1 -> BUY
        result = combine_signals(
            technical={"recommendation": "BUY"},
            prediction={"direction": "DOWN"},
            sentiment={"overall_sentiment": "neutral"},
        )
        assert result["final_recommendation"] == "BUY"
        assert result["weighted_bullish"] == 3
        assert result["weighted_bearish"] == 1
        assert "outweighed" in result["note"]

    def test_ml_and_sentiment_tie_against_neutral_technical_is_hold(self):
        # technical neutral (0), ml bullish (1), sentiment bearish (1) -> tie -> HOLD
        result = combine_signals(
            technical={"recommendation": "HOLD"},
            prediction={"direction": "UP"},
            sentiment={"overall_sentiment": "negative"},
        )
        assert result["final_recommendation"] == "HOLD"
        assert result["weighted_bullish"] == 1
        assert result["weighted_bearish"] == 1
        assert "Result: HOLD" in result["note"]

    def test_technical_sell_outweighs_bullish_ml_and_sentiment(self):
        # technical(SELL, 3) vs ml(UP,1) + sentiment(positive,1) = bullish 2, bearish 3
        result = combine_signals(
            technical={"recommendation": "SELL"},
            prediction={"direction": "UP"},
            sentiment={"overall_sentiment": "positive"},
        )
        assert result["final_recommendation"] == "SELL"
        assert result["weighted_bullish"] == 2
        assert result["weighted_bearish"] == 3

    def test_breakdown_structure_and_weights(self):
        result = combine_signals(
            technical={"recommendation": "BUY", "historical_accuracy": {"success_rate_pct": 61.5}},
            prediction={"direction": "UP", "model_accuracy_on_test_set": 0.5084},
            sentiment={"overall_sentiment": "positive"},
        )
        breakdown = result["breakdown"]
        assert breakdown["technical"]["weight"] == 3
        assert breakdown["ml"]["weight"] == 1
        assert breakdown["sentiment"]["weight"] == 1
        assert breakdown["technical"]["backtested"] == {"success_rate_pct": 61.5}
        assert breakdown["ml"]["model_accuracy"] == 0.5084
        assert result["total_weight"] == 5

    def test_total_weight_is_constant_regardless_of_votes(self):
        result = combine_signals(
            technical={"recommendation": "HOLD"},
            prediction={"direction": "DOWN"},
            sentiment={"overall_sentiment": "neutral"},
        )
        assert result["total_weight"] == 5

from app.services.ensemble import get_final_recommendation


class TestGetFinalRecommendation:
    def test_wires_all_signals_together_and_tags_ticker(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.ensemble.fetch_stock_data",
            lambda ticker, period: pd.DataFrame({"close": [100.0] * 60}),
        )
        monkeypatch.setattr(
            "app.services.ensemble.add_indicators",
            lambda df: df,  # pass-through; indicators tested separately
        )
        monkeypatch.setattr(
            "app.services.ensemble.get_recommendation",
            lambda df: {"recommendation": "BUY", "historical_accuracy": {"success_rate_pct": 60.0}},
        )
        monkeypatch.setattr(
            "app.services.ensemble.predict_direction",
            lambda ticker: {"direction": "UP", "model_accuracy_on_test_set": 0.51},
        )
        monkeypatch.setattr(
            "app.services.ensemble.analyze_ticker_sentiment",
            lambda ticker: {"overall_sentiment": "positive"},
        )

        result = get_final_recommendation("AAPL", timeframe="1Y")

        assert result["ticker"] == "AAPL"
        assert result["final_recommendation"] == "BUY"  # all three bullish

    def test_unknown_timeframe_falls_back_to_1y(self, monkeypatch):
        captured_period = {}

        def fake_fetch(ticker, period):
            captured_period["value"] = period
            return pd.DataFrame({"close": [100.0] * 60})

        monkeypatch.setattr("app.services.ensemble.fetch_stock_data", fake_fetch)
        monkeypatch.setattr("app.services.ensemble.add_indicators", lambda df: df)
        monkeypatch.setattr(
            "app.services.ensemble.get_recommendation",
            lambda df: {"recommendation": "HOLD", "historical_accuracy": None},
        )
        monkeypatch.setattr(
            "app.services.ensemble.predict_direction",
            lambda ticker: {"direction": "DOWN", "model_accuracy_on_test_set": 0.5},
        )
        monkeypatch.setattr(
            "app.services.ensemble.analyze_ticker_sentiment",
            lambda ticker: {"overall_sentiment": "neutral"},
        )

        get_final_recommendation("AAPL", timeframe="not-a-real-timeframe")
        # period_map.get(timeframe, "1y") -- unrecognized key silently defaults to "1y"
        assert captured_period["value"] == "1y"

    @pytest.mark.parametrize("timeframe,expected_period", [
        ("1M", "1mo"), ("3M", "3mo"), ("6M", "6mo"), ("1Y", "1y"), ("5Y", "5y"),
    ])
    def test_timeframe_maps_to_correct_period(self, monkeypatch, timeframe, expected_period):
        captured_period = {}

        def fake_fetch(ticker, period):
            captured_period["value"] = period
            return pd.DataFrame({"close": [100.0] * 60})

        monkeypatch.setattr("app.services.ensemble.fetch_stock_data", fake_fetch)
        monkeypatch.setattr("app.services.ensemble.add_indicators", lambda df: df)
        monkeypatch.setattr(
            "app.services.ensemble.get_recommendation",
            lambda df: {"recommendation": "HOLD", "historical_accuracy": None},
        )
        monkeypatch.setattr(
            "app.services.ensemble.predict_direction",
            lambda ticker: {"direction": "UP", "model_accuracy_on_test_set": 0.5},
        )
        monkeypatch.setattr(
            "app.services.ensemble.analyze_ticker_sentiment",
            lambda ticker: {"overall_sentiment": "neutral"},
        )

        get_final_recommendation("AAPL", timeframe=timeframe)
        assert captured_period["value"] == expected_period