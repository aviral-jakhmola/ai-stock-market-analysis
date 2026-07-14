from transformers import pipeline
from app.services.news_fetcher import fetch_news

# Load FinBERT once, at import time, so it's not reloaded on every request
_sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
)


def analyze_sentiment(text: str) -> dict:
    """
    Runs a single piece of text through FinBERT and returns
    the predicted label (positive/negative/neutral) with a confidence score.
    """
    result = _sentiment_pipeline(text)[0]
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