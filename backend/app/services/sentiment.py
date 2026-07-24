from transformers import pipeline
from app.services.news_fetcher import fetch_news

# FinBERT is loaded lazily, on first actual use — not at import time.
# Importing this module (which happens on every app boot, since routers
# reference it) no longer forces ~500MB-1GB of model weights into memory
# before anyone has made a single sentiment request. This matters most in
# memory-constrained environments (e.g. Railway's 1GB container limit) —
# search/technical/ML-only requests never touch this cost at all.
_sentiment_pipeline = None


def _get_sentiment_pipeline():
    """
    Returns the cached FinBERT pipeline, building it on first call.
    Every call after the first returns the same in-memory instance —
    same performance characteristic as the old module-level load,
    just deferred until actually needed.
    """
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
        )
    return _sentiment_pipeline


def analyze_sentiment(text: str) -> dict:
    """
    Runs a single piece of text through FinBERT and returns
    the predicted label (positive/negative/neutral) with a confidence score.
    """
    sentiment_pipeline = _get_sentiment_pipeline()
    result = sentiment_pipeline(text)[0]
    return {
        "label": result["label"],
        "score": round(result["score"], 4),
    }


def analyze_ticker_sentiment(ticker_symbol: str, limit: int = 10) -> dict:
    """
    Fetches recent news for a ticker and runs each headline through FinBERT.
    Returns per-article sentiment plus an aggregated summary.
    """
    articles = fetch_news(ticker_symbol, limit=limit)

    if not articles:
        return {
            "ticker": ticker_symbol,
            "articles": [],
            "summary": {"positive": 0, "negative": 0, "neutral": 0},
            "overall_sentiment": "neutral",
        }

    scored_articles = []
    counts = {"positive": 0, "negative": 0, "neutral": 0}

    for article in articles:
        if not article["title"]:
            continue
        sentiment = analyze_sentiment(article["title"])
        scored_articles.append({**article, "sentiment": sentiment})
        counts[sentiment["label"]] += 1

    total = sum(counts.values())
    overall = max(counts, key=counts.get) if total > 0 else "neutral"

    return {
        "ticker": ticker_symbol,
        "articles": scored_articles,
        "summary": counts,
        "overall_sentiment": overall,
    }


if __name__ == "__main__":
    result = analyze_ticker_sentiment("RELIANCE.NS")
    print("Overall:", result["overall_sentiment"])
    print("Summary:", result["summary"])
    for a in result["articles"]:
        print(f"  [{a['sentiment']['label']:>8}] {a['title']}")