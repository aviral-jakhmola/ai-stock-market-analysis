import os
import logging
import httpx
from app.services.news_fetcher import fetch_news

logger = logging.getLogger(__name__)

# Hugging Face API Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/ProsusAI/finbert"

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}


async def analyze_sentiment(text: str) -> dict:
    """
    Offloads FinBERT inference to Hugging Face Serverless API via async HTTP.
    Saves ~800MB-1GB container RAM on memory-constrained hosts (e.g. Railway).
    """
    if not text or not text.strip():
        return {"label": "neutral", "score": 0.5}

    if not HF_API_TOKEN:
        logger.warning("HF_API_TOKEN is not set in environment. Falling back to neutral.")
        return {"label": "neutral", "score": 0.5}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                HF_API_URL,
                headers=HEADERS,
                json={"inputs": text}
            )

            # Handle Hugging Face model cold-start state
            if response.status_code == 503:
                logger.warning("FinBERT model is cold-starting on HF servers. Returning neutral fallback.")
                return {"label": "neutral", "score": 0.5}

            response.raise_for_status()
            data = response.json()

            # Handle Hugging Face response structure
            predictions = (
                data[0]
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list)
                else data
            )

            if not isinstance(predictions, list):
                return {"label": "neutral", "score": 0.5}

            # Select prediction with highest score
            top_prediction = max(predictions, key=lambda x: x.get("score", 0))

            return {
                "label": top_prediction.get("label", "neutral").lower(),
                "score": round(top_prediction.get("score", 0.5), 4)
            }

    except Exception as e:
        logger.error(f"Error querying Hugging Face Sentiment API: {e}")
        return {"label": "neutral", "score": 0.5}


async def analyze_ticker_sentiment(ticker_symbol: str, limit: int = 10) -> dict:
    """
    Fetches recent news for a ticker symbol and calculates per-article and overall
    sentiment using async FinBERT API calls.
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
        title = article.get("title")
        if not title:
            continue

        # Correctly await the async analyze_sentiment function
        sentiment = await analyze_sentiment(title)
        scored_articles.append({**article, "sentiment": sentiment})

        label = sentiment.get("label", "neutral")
        if label in counts:
            counts[label] += 1
        else:
            counts["neutral"] += 1

    total = sum(counts.values())
    overall = max(counts, key=counts.get) if total > 0 else "neutral"

    return {
        "ticker": ticker_symbol,
        "articles": scored_articles,
        "summary": counts,
        "overall_sentiment": overall,
    }


if __name__ == "__main__":
    import asyncio

    async def main():
        result = await analyze_ticker_sentiment("RELIANCE.NS")
        print("Overall Sentiment:", result["overall_sentiment"])
        print("Summary Counts:", result["summary"])
        for a in result["articles"]:
            print(f"  [{a['sentiment']['label']:>8}] {a['title']}")

    asyncio.run(main())