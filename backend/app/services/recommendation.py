import pandas as pd


def generate_signal(row: pd.Series) -> dict:
    """
    Looks at one row's indicator values and returns individual votes
    plus an overall BUY/HOLD/SELL recommendation.
    """
    votes = []

    # --- RSI ---
    if pd.notnull(row.get("rsi_14")):
        rsi_val = row["rsi_14"]
        if rsi_val < 30:
            votes.append({
                "indicator": "RSI",
                "direction": "bullish",
                "value": round(rsi_val, 1),
                "text": "Oversold",
                "why": "RSI below 30 suggests the stock has fallen further/faster than usual and may be due for a bounce.",
            })
        elif rsi_val > 70:
            votes.append({
                "indicator": "RSI",
                "direction": "bearish",
                "value": round(rsi_val, 1),
                "text": "Overbought",
                "why": "RSI above 70 suggests the stock has risen further/faster than usual and may be due for a pullback.",
            })
        else:
            votes.append({
                "indicator": "RSI",
                "direction": "neutral",
                "value": round(rsi_val, 1),
                "text": "Neutral range",
                "why": "RSI between 30 and 70 indicates neither overbought nor oversold conditions.",
            })

    # --- MACD ---
    if pd.notnull(row.get("macd")) and pd.notnull(row.get("macd_histogram")):
        macd_val = row["macd"]
        if row["macd_histogram"] > 0:
            votes.append({
                "indicator": "MACD",
                "direction": "bullish",
                "value": round(macd_val, 2),
                "text": "Above signal line",
                "why": "MACD crossing above its signal line suggests upward momentum is building.",
            })
        else:
            votes.append({
                "indicator": "MACD",
                "direction": "bearish",
                "value": round(macd_val, 2),
                "text": "Below signal line",
                "why": "MACD below its signal line suggests downward momentum or fading strength.",
            })

    # --- Trend (price vs EMAs) ---
    if pd.notnull(row.get("ema_20")) and pd.notnull(row.get("ema_50")):
        close = row["close"]
        pct_vs_ema20 = ((close - row["ema_20"]) / row["ema_20"]) * 100
        if close > row["ema_20"] and close > row["ema_50"]:
            votes.append({
                "indicator": "Trend",
                "direction": "bullish",
                "value": f"{pct_vs_ema20:+.1f}%",
                "text": "Above both EMA 20 & 50",
                "why": "Price trading above both moving averages suggests an established uptrend.",
            })
        elif close < row["ema_20"] and close < row["ema_50"]:
            votes.append({
                "indicator": "Trend",
                "direction": "bearish",
                "value": f"{pct_vs_ema20:+.1f}%",
                "text": "Below both EMA 20 & 50",
                "why": "Price trading below both moving averages suggests an established downtrend.",
            })
        else:
            votes.append({
                "indicator": "Trend",
                "direction": "neutral",
                "value": f"{pct_vs_ema20:+.1f}%",
                "text": "Between EMA 20 & 50",
                "why": "Price sitting between the two moving averages suggests no clear trend direction yet.",
            })

    # --- Bollinger Bands ---
    if pd.notnull(row.get("bb_upper")) and pd.notnull(row.get("bb_lower")):
        close = row["close"]
        band_width = row["bb_upper"] - row["bb_lower"]
        if band_width > 0:
            position = (close - row["bb_lower"]) / band_width
            if position < 0.2:
                votes.append({
                    "indicator": "Bollinger",
                    "direction": "bullish",
                    "value": f"{position * 100:.0f}%",
                    "text": "Near lower band",
                    "why": "Price near the lower band suggests the stock is stretched to the downside relative to recent volatility.",
                })
            elif position > 0.8:
                votes.append({
                    "indicator": "Bollinger",
                    "direction": "bearish",
                    "value": f"{position * 100:.0f}%",
                    "text": "Near upper band",
                    "why": "Price near the upper band suggests the stock is stretched to the upside relative to recent volatility.",
                })
            else:
                votes.append({
                    "indicator": "Bollinger",
                    "direction": "neutral",
                    "value": f"{position * 100:.0f}%",
                    "text": "Within normal range",
                    "why": "Price sitting within the bands suggests normal, non-extreme volatility conditions.",
                })

    # --- Combine votes into final recommendation ---
    bullish_count = sum(1 for v in votes if v["direction"] == "bullish")
    bearish_count = sum(1 for v in votes if v["direction"] == "bearish")

    if bullish_count >= 2 and bullish_count > bearish_count:
        recommendation = "BUY"
    elif bearish_count >= 2 and bearish_count > bullish_count:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "recommendation": recommendation,
        "votes": votes,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "total_votes": len(votes),
    }

def backtest_signals(df: pd.DataFrame, lookahead_days: int = 5) -> dict:
    """
    Replays the signal-generation rules across historical data to measure
    how often each signal type was historically followed by a correct outcome.

    For BUY signals: "correct" means price was higher after `lookahead_days`.
    For SELL signals: "correct" means price was lower after `lookahead_days`.
    HOLD signals aren't scored, since there's no directional bet to check.
    """
    results = {
        "BUY": {"correct": 0, "total": 0},
        "SELL": {"correct": 0, "total": 0},
    }

    usable_range = len(df) - lookahead_days

    for i in range(usable_range):
        row = df.iloc[i]
        signal = generate_signal(row)
        rec = signal["recommendation"]

        if rec not in ("BUY", "SELL"):
            continue

        current_close = row["close"]
        future_close = df.iloc[i + lookahead_days]["close"]

        price_went_up = future_close > current_close

        results[rec]["total"] += 1

        if rec == "BUY" and price_went_up:
            results[rec]["correct"] += 1
        elif rec == "SELL" and not price_went_up:
            results[rec]["correct"] += 1

    summary = {}
    for signal_type, counts in results.items():
        total = counts["total"]
        correct = counts["correct"]
        success_rate = (correct / total * 100) if total > 0 else None

        summary[signal_type] = {
            "sample_size": total,
            "success_rate_pct": round(success_rate, 1) if success_rate is not None else None,
            "reliable": total >= 10,
        }

    return summary


def get_recommendation(df: pd.DataFrame, lookahead_days: int = 5) -> dict:
    latest_row = df.iloc[-1]
    signal = generate_signal(latest_row)

    backtest = backtest_signals(df, lookahead_days=lookahead_days)

    recommendation = signal["recommendation"]
    historical = backtest.get(recommendation)

    return {
        "recommendation": recommendation,
        "votes": signal["votes"],
        "signal_strength": {
            "bullish_votes": signal["bullish_count"],
            "bearish_votes": signal["bearish_count"],
            "total_votes": signal["total_votes"],
            "agreement_pct": round(
                max(signal["bullish_count"], signal["bearish_count"])
                / signal["total_votes"] * 100, 1
            ) if signal["total_votes"] > 0 else None,
        },
        "historical_accuracy": historical,
        "lookahead_days": lookahead_days,
    }