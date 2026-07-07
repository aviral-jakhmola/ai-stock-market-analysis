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


@router.get(
    "/{ticker}/history",
    response_model=list[StockHistory]
)
def get_history(
    ticker: str,
    timeframe: str = "1Y"
):
    period_map = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y"
    }

    if timeframe not in period_map:
        raise HTTPException(
            status_code=400,
            detail="Invalid timeframe"
        )

    try:

        df = fetch_stock_data(
            ticker=ticker,
            period=period_map[timeframe]
        )

        return df.to_dict(orient="records")

    except Exception:

        raise HTTPException(
            status_code=404,
            detail="Ticker not found"
        )