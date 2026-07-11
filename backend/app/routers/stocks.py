from fastapi import APIRouter, HTTPException

from app.services.data_fetcher import fetch_stock_data
from app.schemas.stock import StockHistory

router = APIRouter(
    prefix="/api/stocks",
    tags=["Stocks"]
)

AVAILABLE_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "AAPL",
    "INFY.NS",
    "HDFCBANK.NS"
]


@router.get("/search")
def search_stock(q: str):
    results = [
        stock
        for stock in AVAILABLE_STOCKS
        if q.upper() in stock
    ]

    return {
        "query": q,
        "results": results
    }


@router.get("/{ticker}/history", response_model=list[StockHistory])
def get_history(ticker: str, timeframe: str = "1Y"):
    period_map = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y",
        "5Y": "5y",
    }

    if timeframe not in period_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeframe '{timeframe}'. Must be one of {list(period_map.keys())}."
        )

    try:
        df = fetch_stock_data(ticker=ticker, period=period_map[timeframe])
        return df.to_dict(orient="records")
    except ValueError as e:
        # e.g. no data found for ticker
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))