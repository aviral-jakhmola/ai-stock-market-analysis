import yfinance as yf


def fetch_news(ticker_symbol: str, limit: int = 10) -> list[dict]:
    """
    Fetches recent news articles for a ticker via yfinance.
    Returns a simplified list of {title, publisher, link, published} dicts.
    """
    ticker = yf.Ticker(ticker_symbol)
    raw_news = ticker.news

    if not raw_news:
        return []

    articles = []
    for item in raw_news[:limit]:
        content = item.get("content", item)  # yfinance news structure varies by version
        articles.append({
            "title": content.get("title"),
            "publisher": content.get("provider", {}).get("displayName") if isinstance(content.get("provider"), dict) else content.get("publisher"),
            "link": content.get("canonicalUrl", {}).get("url") if isinstance(content.get("canonicalUrl"), dict) else content.get("link"),
            "published": content.get("pubDate") or content.get("providerPublishTime"),
        })

    return articles


if __name__ == "__main__":
    news = fetch_news("RELIANCE.NS")
    for article in news:
        print(article)