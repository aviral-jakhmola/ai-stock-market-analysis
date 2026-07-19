from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators
from app.services.recommendation import get_recommendation
from app.services.ml_predictor import predict_direction
from app.services.sentiment import analyze_ticker_sentiment


def get_final_recommendation(ticker: str, timeframe: str = "1Y") -> dict:
    """
    Fetches technical, ML, and sentiment signals for a ticker and combines
    them into one final weighted recommendation.
    """
    period_map = {
        "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y",
    }
    period = period_map.get(timeframe, "1y")

    df = fetch_stock_data(ticker=ticker, period=period)
    df = add_indicators(df)

    technical = get_recommendation(df)
    prediction = predict_direction(ticker)
    sentiment = analyze_ticker_sentiment(ticker)

    combined = combine_signals(technical, prediction, sentiment)
    combined["ticker"] = ticker

    return combined


def _technical_vote(technical: dict) -> str:
    """
    Converts the rule-based recommendation into a simple bullish/bearish/neutral vote.
    """
    rec = technical.get("recommendation")
    if rec == "BUY":
        return "bullish"
    elif rec == "SELL":
        return "bearish"
    return "neutral"


def _ml_vote(prediction: dict) -> str:
    """
    Converts the ML classifier's direction into a vote. Since accuracy sits
    close to chance (~50%), this vote carries real but modest weight — it's
    not being treated as a strong signal.
    """
    direction = prediction.get("direction")
    return "bullish" if direction == "UP" else "bearish"


def _sentiment_vote(sentiment: dict) -> str:
    """
    Converts overall news sentiment into a vote.
    """
    overall = sentiment.get("overall_sentiment")
    if overall == "positive":
        return "bullish"
    elif overall == "negative":
        return "bearish"
    return "neutral"


# Weights reflect how much each signal type has actually been validated.
# Technical: backtested per-signal historically (Milestone 3).
# ML: real probability, but accuracy measured close to chance (Milestone 6).
# Sentiment: real NLP signal, but never backtested against price outcomes.
WEIGHTS = {
    "technical": 3,
    "ml": 1,
    "sentiment": 1,
}


def _build_note(votes: dict, final_recommendation: str, bullish_weight: int, bearish_weight: int) -> str:
    """
    Generates a short, honest explanation of how the final call was reached,
    especially useful when signals disagree with each other.
    """
    bullish_sources = [k for k, v in votes.items() if v == "bullish"]
    bearish_sources = [k for k, v in votes.items() if v == "bearish"]
    neutral_sources = [k for k, v in votes.items() if v == "neutral"]

    all_agree = len(set(votes.values())) == 1

    if all_agree:
        direction = votes["technical"]
        return f"All three signals agree ({direction})."

    if bullish_weight == bearish_weight:
        return (
            f"Signals are split — {', '.join(bullish_sources) or 'none'} bullish, "
            f"{', '.join(bearish_sources) or 'none'} bearish, "
            f"{', '.join(neutral_sources) or 'none'} neutral. "
            f"Result: HOLD, since no side has more weighted support."
        )

    winning_side = "bullish" if bullish_weight > bearish_weight else "bearish"
    winning_sources = bullish_sources if winning_side == "bullish" else bearish_sources
    opposing_sources = bearish_sources if winning_side == "bullish" else bullish_sources

    note = f"{', '.join(winning_sources)} {winning_side} outweighed "
    if opposing_sources:
        note += f"{', '.join(opposing_sources)} {'bearish' if winning_side == 'bullish' else 'bullish'} "
    else:
        note += "no opposing signal "
    note += f"({winning_side} weight {max(bullish_weight, bearish_weight)} vs {min(bullish_weight, bearish_weight)})."

    if neutral_sources:
        note += f" {', '.join(neutral_sources)} stayed neutral."

    return note


def combine_signals(technical: dict, prediction: dict, sentiment: dict) -> dict:
    """
    Combines the three independently-built signal sources into one final
    recommendation using weighted voting. Technical carries the most weight
    since it's the only backtested signal; ML and sentiment contribute less,
    reflecting their honestly lower validation.
    """
    votes = {
        "technical": _technical_vote(technical),
        "ml": _ml_vote(prediction),
        "sentiment": _sentiment_vote(sentiment),
    }

    bullish_weight = sum(WEIGHTS[k] for k, v in votes.items() if v == "bullish")
    bearish_weight = sum(WEIGHTS[k] for k, v in votes.items() if v == "bearish")
    total_weight = sum(WEIGHTS.values())

    if bullish_weight > bearish_weight:
        final_recommendation = "BUY"
    elif bearish_weight > bullish_weight:
        final_recommendation = "SELL"
    else:
        final_recommendation = "HOLD"

    note = _build_note(votes, final_recommendation, bullish_weight, bearish_weight)

    return {
        "final_recommendation": final_recommendation,
        "note": note,
        "breakdown": {
            "technical": {
                "vote": votes["technical"],
                "weight": WEIGHTS["technical"],
                "detail": technical.get("recommendation"),
                "backtested": technical.get("historical_accuracy"),
            },
            "ml": {
                "vote": votes["ml"],
                "weight": WEIGHTS["ml"],
                "detail": prediction.get("direction"),
                "model_accuracy": prediction.get("model_accuracy_on_test_set"),
            },
            "sentiment": {
                "vote": votes["sentiment"],
                "weight": WEIGHTS["sentiment"],
                "detail": sentiment.get("overall_sentiment"),
            },
        },
        "weighted_bullish": bullish_weight,
        "weighted_bearish": bearish_weight,
        "total_weight": total_weight,
    }


if __name__ == "__main__":
    mock_technical = {
        "recommendation": "BUY",
        "historical_accuracy": {"sample_size": 39, "success_rate_pct": 61.5, "reliable": True},
    }
    mock_prediction = {
        "direction": "DOWN",
        "model_accuracy_on_test_set": 0.5084,
    }
    mock_sentiment = {
        "overall_sentiment": "neutral",
    }

    result = combine_signals(mock_technical, mock_prediction, mock_sentiment)
    print(result["final_recommendation"])
    print(result["note"])