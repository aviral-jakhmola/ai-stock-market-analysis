import yfinance as yf


def fetch_company_overview(ticker_symbol: str) -> dict:
    """
    Fetches fundamental company data (sector, market cap, P/E, etc.)
    for a given ticker using yfinance.
    """
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    if not info or info.get("longName") is None:
        raise ValueError(f"No company data found for {ticker_symbol}")

    return {
        "name": info.get("longName") or info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "currency": info.get("currency"),
    }

if __name__ == "__main__":
    data = fetch_company_overview("RELIANCE.NS")
    print(data)