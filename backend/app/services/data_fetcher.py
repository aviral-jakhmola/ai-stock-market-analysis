
import os

import pandas as pd
import yfinance as yf


# ----------------------------
# Configuration
# ----------------------------

DATA_FOLDER = "../data"

os.makedirs(DATA_FOLDER, exist_ok=True)


# ----------------------------
# Fetch Function
# ----------------------------

def fetch_stock_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
):
    """
    Download stock data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Stock symbol
    period : str
        Example: 1mo, 3mo, 6mo, 1y, 5y
    interval : str
        Example: 1d, 1wk, 1mo

    Returns
    -------
    pandas.DataFrame
    """

    print(f"\nDownloading {ticker}...")

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    # Convert index into Date column
    df.reset_index(inplace=True)

    # Flatten MultiIndex columns if yfinance returns them
    # (common in yfinance 1.x even for a single ticker)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    print("\nColumns:")
    print(df.columns.tolist())

    # Rename columns
    df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        },
        inplace=True,
    )

    # Convert to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Remove missing values
    df.dropna(inplace=True)

    # Keep required columns
    df = df[
        [
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ]

    return df


# ----------------------------
# Save CSV
# ----------------------------

def save_csv(df: pd.DataFrame, ticker: str):

    filename = ticker.replace(".", "_") + ".csv"

    filepath = os.path.join(DATA_FOLDER, filename)

    df.to_csv(filepath, index=False)

    print(f"Saved -> {filepath}")


# ----------------------------
# Test
# ----------------------------

if __name__ == "__main__":

    tickers = [
        "RELIANCE.NS",
        "TCS.NS",
        "AAPL",
    ]

    for ticker in tickers:

        try:

            data = fetch_stock_data(
                ticker=ticker,
                period="1y",
                interval="1d",
            )

            print(data.head())

            save_csv(data, ticker)

            print("-" * 60)

        except Exception as e:

            print(f"Error downloading {ticker}")

            print(e)