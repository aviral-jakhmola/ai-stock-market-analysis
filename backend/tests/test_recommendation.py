import pandas as pd
import pytest

from app.services.recommendation import generate_signal, backtest_signals, get_recommendation

pytestmark = pytest.mark.unit


def make_row(**overrides):
    """Row with every indicator defaulted to missing; override just what a test needs."""
    base = {
        "close": 100.0,
        "rsi_14": None,
        "macd": None,
        "macd_histogram": None,
        "ema_20": None,
        "ema_50": None,
        "bb_upper": None,
        "bb_lower": None,
    }
    base.update(overrides)
    return pd.Series(base)


def find_vote(votes, indicator):
    return next((v for v in votes if v["indicator"] == indicator), None)


class TestRSIVote:
    def test_oversold_is_bullish(self):
        signal = generate_signal(make_row(rsi_14=25))
        vote = find_vote(signal["votes"], "RSI")
        assert vote["direction"] == "bullish"
        assert vote["text"] == "Oversold"

    def test_overbought_is_bearish(self):
        signal = generate_signal(make_row(rsi_14=75))
        vote = find_vote(signal["votes"], "RSI")
        assert vote["direction"] == "bearish"

    def test_midrange_is_neutral(self):
        signal = generate_signal(make_row(rsi_14=50))
        vote = find_vote(signal["votes"], "RSI")
        assert vote["direction"] == "neutral"

    def test_missing_rsi_casts_no_vote(self):
        signal = generate_signal(make_row(rsi_14=None))
        assert find_vote(signal["votes"], "RSI") is None


class TestMACDVote:
    def test_positive_histogram_is_bullish(self):
        signal = generate_signal(make_row(macd=1.0, macd_histogram=0.5))
        vote = find_vote(signal["votes"], "MACD")
        assert vote["direction"] == "bullish"

    def test_negative_histogram_is_bearish(self):
        signal = generate_signal(make_row(macd=-1.0, macd_histogram=-0.2))
        vote = find_vote(signal["votes"], "MACD")
        assert vote["direction"] == "bearish"

    def test_exactly_zero_histogram_is_bearish(self):
        # Documents current behavior: condition is `> 0`, so histogram == 0
        # falls into the bearish branch, not a neutral one (MACD has no neutral vote at all).
        signal = generate_signal(make_row(macd=0.0, macd_histogram=0.0))
        vote = find_vote(signal["votes"], "MACD")
        assert vote["direction"] == "bearish"

    def test_missing_macd_casts_no_vote(self):
        signal = generate_signal(make_row(macd=None, macd_histogram=None))
        assert find_vote(signal["votes"], "MACD") is None


class TestTrendVote:
    def test_above_both_emas_is_bullish(self):
        signal = generate_signal(make_row(close=110, ema_20=105, ema_50=100))
        vote = find_vote(signal["votes"], "Trend")
        assert vote["direction"] == "bullish"
        assert vote["value"] == "+4.8%"

    def test_below_both_emas_is_bearish(self):
        signal = generate_signal(make_row(close=90, ema_20=95, ema_50=100))
        vote = find_vote(signal["votes"], "Trend")
        assert vote["direction"] == "bearish"
        assert vote["value"] == "-5.3%"

    def test_between_emas_is_neutral(self):
        signal = generate_signal(make_row(close=100, ema_20=105, ema_50=95))
        vote = find_vote(signal["votes"], "Trend")
        assert vote["direction"] == "neutral"

    def test_missing_ema_casts_no_vote(self):
        signal = generate_signal(make_row(ema_20=None, ema_50=None))
        assert find_vote(signal["votes"], "Trend") is None


class TestBollingerVote:
    def test_near_lower_band_is_bullish(self):
        signal = generate_signal(make_row(close=101, bb_lower=100, bb_upper=110))
        vote = find_vote(signal["votes"], "Bollinger")
        assert vote["direction"] == "bullish"
        assert vote["value"] == "10%"

    def test_near_upper_band_is_bearish(self):
        signal = generate_signal(make_row(close=109, bb_lower=100, bb_upper=110))
        vote = find_vote(signal["votes"], "Bollinger")
        assert vote["direction"] == "bearish"
        assert vote["value"] == "90%"

    def test_middle_of_band_is_neutral(self):
        signal = generate_signal(make_row(close=105, bb_lower=100, bb_upper=110))
        vote = find_vote(signal["votes"], "Bollinger")
        assert vote["direction"] == "neutral"

    def test_zero_width_band_casts_no_vote(self):
        # Documents current behavior: bb_upper == bb_lower makes band_width == 0,
        # which the `if band_width > 0` guard skips entirely (no vote, not an error).
        signal = generate_signal(make_row(close=100, bb_lower=100, bb_upper=100))
        assert find_vote(signal["votes"], "Bollinger") is None

    def test_missing_bands_cast_no_vote(self):
        signal = generate_signal(make_row(bb_upper=None, bb_lower=None))
        assert find_vote(signal["votes"], "Bollinger") is None


class TestOverallRecommendation:
    def test_two_bullish_no_bearish_is_buy(self):
        row = make_row(rsi_14=25, close=110, ema_20=105, ema_50=100)
        signal = generate_signal(row)
        assert signal["bullish_count"] == 2
        assert signal["bearish_count"] == 0
        assert signal["recommendation"] == "BUY"

    def test_two_bearish_beats_one_bullish(self):
        row = make_row(
            rsi_14=25,  # bullish
            macd=-1.0, macd_histogram=-0.5,  # bearish
            close=90, ema_20=95, ema_50=100,  # bearish trend
        )
        signal = generate_signal(row)
        assert signal["bullish_count"] == 1
        assert signal["bearish_count"] == 2
        assert signal["recommendation"] == "SELL"

    def test_two_two_tie_is_hold(self):
        row = make_row(
            rsi_14=25,                                  # bullish
            close=109, ema_20=105, ema_50=100,           # bullish trend
            macd=-1.0, macd_histogram=-0.1,              # bearish
            bb_lower=90, bb_upper=110,                   # bearish bollinger (position 0.95)
        )
        signal = generate_signal(row)
        assert signal["bullish_count"] == 2
        assert signal["bearish_count"] == 2
        assert signal["recommendation"] == "HOLD"

    def test_single_bullish_vote_is_hold_not_buy(self):
        # bullish_count must be >= 2, not just > bearish_count
        row = make_row(rsi_14=25)
        signal = generate_signal(row)
        assert signal["bullish_count"] == 1
        assert signal["recommendation"] == "HOLD"

    def test_all_neutral_is_hold(self):
        row = make_row(rsi_14=50, close=100, ema_20=105, ema_50=95)
        signal = generate_signal(row)
        assert signal["recommendation"] == "HOLD"


class TestBacktestSignals:
    def test_success_rates_on_monotonic_uptrend(self, monkeypatch):
        # Alternate BUY/SELL by row position regardless of indicator content,
        # so the test isolates backtest_signals' scoring logic from generate_signal's voting logic.
        def fake_signal(row):
            rec = "BUY" if row.name % 2 == 0 else "SELL"
            return {"recommendation": rec, "votes": [], "bullish_count": 0, "bearish_count": 0, "total_votes": 0}

        monkeypatch.setattr("app.services.recommendation.generate_signal", fake_signal)

        # Strictly increasing closes -> price is always up over any lookahead window.
        df = pd.DataFrame({"close": list(range(1, 21))})  # 20 rows, index 0..19
        summary = backtest_signals(df, lookahead_days=5)

        # usable_range = 20 - 5 = 15 -> i in 0..14
        # evens (BUY): 0,2,4,6,8,10,12,14 -> 8 total, all correct (price went up)
        # odds (SELL): 1,3,5,7,9,11,13 -> 7 total, 0 correct (price went up, not down)
        assert summary["BUY"] == {"sample_size": 8, "success_rate_pct": 100.0, "reliable": False}
        assert summary["SELL"] == {"sample_size": 7, "success_rate_pct": 0.0, "reliable": False}

    def test_reliable_flag_true_once_sample_size_hits_ten(self, monkeypatch):
        def fake_signal(row):
            rec = "BUY" if row.name % 2 == 0 else "SELL"
            return {"recommendation": rec, "votes": [], "bullish_count": 0, "bearish_count": 0, "total_votes": 0}

        monkeypatch.setattr("app.services.recommendation.generate_signal", fake_signal)

        df = pd.DataFrame({"close": list(range(1, 41))})  # 40 rows
        summary = backtest_signals(df, lookahead_days=5)
        assert summary["BUY"]["sample_size"] >= 10
        assert summary["BUY"]["reliable"] is True
        assert summary["SELL"]["reliable"] is True

    def test_hold_signals_are_not_scored(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.recommendation.generate_signal",
            lambda row: {"recommendation": "HOLD", "votes": [], "bullish_count": 0, "bearish_count": 0, "total_votes": 0},
        )
        df = pd.DataFrame({"close": list(range(1, 21))})
        summary = backtest_signals(df, lookahead_days=5)
        assert summary["BUY"]["sample_size"] == 0
        assert summary["BUY"]["success_rate_pct"] is None
        assert summary["SELL"]["sample_size"] == 0


class TestGetRecommendation:
    def test_historical_accuracy_present_when_final_call_is_buy(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.recommendation.generate_signal",
            lambda row: {
                "recommendation": "BUY",
                "votes": [{"indicator": "RSI", "direction": "bullish", "value": 20, "text": "x", "why": "y"}],
                "bullish_count": 1, "bearish_count": 0, "total_votes": 1,
            },
        )
        df = pd.DataFrame({"close": list(range(1, 31))})
        result = get_recommendation(df, lookahead_days=3)
        assert result["recommendation"] == "BUY"
        assert result["historical_accuracy"] is not None
        assert "sample_size" in result["historical_accuracy"]

    def test_historical_accuracy_is_none_when_final_call_is_hold(self, monkeypatch):
        # Documents an edge case worth knowing about: backtest_signals only ever
        # tracks "BUY"/"SELL" keys, so when the latest row's call is HOLD,
        # backtest.get("HOLD") returns None -- historical_accuracy is None, not an error.
        monkeypatch.setattr(
            "app.services.recommendation.generate_signal",
            lambda row: {"recommendation": "HOLD", "votes": [], "bullish_count": 0, "bearish_count": 0, "total_votes": 0},
        )
        df = pd.DataFrame({"close": list(range(1, 21))})
        result = get_recommendation(df, lookahead_days=2)
        assert result["recommendation"] == "HOLD"
        assert result["historical_accuracy"] is None
        assert result["signal_strength"]["agreement_pct"] is None  # total_votes == 0

    def test_agreement_pct_calculation(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.recommendation.generate_signal",
            lambda row: {"recommendation": "BUY", "votes": [1, 2, 3], "bullish_count": 2, "bearish_count": 1, "total_votes": 3},
        )
        df = pd.DataFrame({"close": list(range(1, 21))})
        result = get_recommendation(df, lookahead_days=2)
        assert result["signal_strength"]["agreement_pct"] == pytest.approx(66.7, abs=0.05)