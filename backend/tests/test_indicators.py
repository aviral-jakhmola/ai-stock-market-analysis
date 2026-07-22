import pandas as pd
import pytest

from app.services.indicators import (
    add_sma,
    add_ema,
    add_rsi,
    add_macd,
    add_bollinger_bands,
    add_indicators,
    add_moving_averages,
)

pytestmark = pytest.mark.unit


def make_df(closes):
    return pd.DataFrame({"close": closes})


class TestSMA:
    def test_known_values(self):
        # SMA(3) of [1,2,3,4,5] -> [nan, nan, 2.0, 3.0, 4.0]
        df = make_df([1, 2, 3, 4, 5])
        df = add_sma(df, period=3)
        result = df["sma_3"].tolist()
        assert result[0] != result[0]  # NaN check (NaN != NaN)
        assert result[1] != result[1]
        assert result[2] == pytest.approx(2.0)
        assert result[3] == pytest.approx(3.0)
        assert result[4] == pytest.approx(4.0)

    def test_column_naming(self):
        df = make_df([1, 2, 3, 4, 5])
        df = add_sma(df, period=20)
        assert "sma_20" in df.columns


class TestEMA:
    def test_matches_manual_recurrence(self):
        # EMA formula: ema[0] = close[0]; ema[t] = alpha*close[t] + (1-alpha)*ema[t-1]
        # where alpha = 2 / (span + 1). Computed independently here to catch
        # accidental changes to the pandas call (adjust=False, span value, etc).
        closes = [10, 12, 11, 14, 13, 15]
        span = 3
        alpha = 2 / (span + 1)

        expected = [closes[0]]
        for price in closes[1:]:
            expected.append(alpha * price + (1 - alpha) * expected[-1])

        df = make_df(closes)
        df = add_ema(df, period=span)
        actual = df[f"ema_{span}"].tolist()

        for exp, act in zip(expected, actual):
            assert act == pytest.approx(exp)


class TestRSI:
    def test_all_gains_is_100(self):
        # Strictly increasing prices -> no losses -> RSI should approach 100
        closes = list(range(1, 20))  # 1..19, strictly increasing
        df = make_df(closes)
        df = add_rsi(df, period=14)
        last_rsi = df["rsi_14"].iloc[-1]
        assert last_rsi == pytest.approx(100.0, abs=0.01)

    def test_all_losses_is_0(self):
        closes = list(range(19, 0, -1))  # strictly decreasing
        df = make_df(closes)
        df = add_rsi(df, period=14)
        last_rsi = df["rsi_14"].iloc[-1]
        assert last_rsi == pytest.approx(0.0, abs=0.01)

    def test_flat_prices_no_crash(self):
        # No gains, no losses -> avg_loss is 0 -> division by zero risk.
        # This documents current behavior rather than asserting a "correct"
        # value; if this starts raising, that's a regression worth knowing about.
        closes = [10.0] * 20
        df = make_df(closes)
        df = add_rsi(df, period=14)
        # Should not raise. RSI on flat prices is NaN/inf depending on how
        # pandas handles 0/0 — just confirm no exception propagated.
        assert "rsi_14" in df.columns


class TestMACD:
    def test_columns_present(self):
        closes = [float(x) for x in range(1, 60)]
        df = make_df(closes)
        df = add_macd(df)
        assert {"macd", "macd_signal", "macd_histogram"}.issubset(df.columns)

    def test_histogram_equals_macd_minus_signal(self):
        closes = [10, 12, 11, 14, 13, 15, 17, 16, 18, 20] * 4
        df = make_df([float(c) for c in closes])
        df = add_macd(df)
        diff = df["macd"] - df["macd_signal"]
        pd.testing.assert_series_equal(
            df["macd_histogram"], diff, check_names=False
        )


class TestBollingerBands:
    def test_middle_band_is_sma(self):
        closes = [float(x) for x in range(1, 30)]
        df = make_df(closes)
        df = add_bollinger_bands(df, period=20)
        expected_middle = pd.Series(closes).rolling(window=20).mean()
        pd.testing.assert_series_equal(
            df["bb_middle"], expected_middle, check_names=False
        )

    def test_upper_above_lower(self):
        closes = [10, 12, 9, 15, 11, 14, 8, 13, 16, 10, 12, 15, 9, 11, 14, 13, 10, 12, 16, 15]
        df = make_df([float(c) for c in closes])
        df = add_bollinger_bands(df, period=20)
        last_row = df.iloc[-1]
        assert last_row["bb_upper"] > last_row["bb_middle"] > last_row["bb_lower"]


class TestAddIndicators:
    def test_full_pipeline_has_all_columns(self):
        # Needs at least 50 rows for sma_50/ema_50 to have any non-NaN values
        closes = [float(100 + (x % 7) - 3) for x in range(80)]
        df = make_df(closes)
        df = add_indicators(df)

        expected_columns = {
            "sma_20", "sma_50", "ema_20", "ema_50",
            "rsi_14", "macd", "macd_signal", "macd_histogram",
            "bb_middle", "bb_upper", "bb_lower",
        }
        assert expected_columns.issubset(df.columns)
        # And the tail (past all warmup periods) should have real numbers, not NaN
        last_row = df.iloc[-1]
        for col in expected_columns:
            assert last_row[col] == last_row[col]  # not NaN

    def test_add_moving_averages_subset(self):
        closes = [float(x) for x in range(60)]
        df = make_df(closes)
        df = add_moving_averages(df)
        assert {"sma_20", "sma_50", "ema_20", "ema_50"}.issubset(df.columns)
        assert "rsi_14" not in df.columns  # this helper shouldn't add RSI