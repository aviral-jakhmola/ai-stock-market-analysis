from fastapi import APIRouter, HTTPException
import pandas as pd

from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators
from app.services.recommendation import get_recommendation

from app.services.company_info import fetch_company_overview
from app.schemas.stock import StockHistory, CompanyOverview

from app.services.sentiment import analyze_ticker_sentiment
from app.schemas.stock import StockHistory, CompanyOverview, SentimentSummary

from app.services.ml_predictor import predict_direction
from app.schemas.stock import StockHistory, CompanyOverview, SentimentSummary, DirectionPrediction


router = APIRouter(
    prefix="/api/stocks",
    tags=["Stocks"]
)

AVAILABLE_STOCKS = [
    # Indian large-caps (NSE)
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "WIPRO.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "ASIANPAINT.NS",
    "HCLTECH.NS",
    "BAJFINANCE.NS",
    "ADANIENT.NS",

    # US large-caps
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "META",
    "NVDA",
    "NFLX",
    "JPM",
    "V",
]


@router.get("/company/{symbol}", response_model=CompanyOverview)
def get_company_overview(symbol: str):
    try:
        return fetch_company_overview(symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/search")
def search_stock(q: str):
    results = [
        stock
        for stock in AVAILABLE_STOCKS
        if q.upper() in stock
    ]
    return {"query": q, "results": results}


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
        df = add_indicators(df)

        df = df.where(pd.notnull(df), None)

        return df.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/recommendation")
def get_stock_recommendation(ticker: str, timeframe: str = "1Y"):
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
        df = add_indicators(df)
        return get_recommendation(df)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{ticker}/sentiment", response_model=SentimentSummary)
def get_stock_sentiment(ticker: str, limit: int = 10):
    try:
        return analyze_ticker_sentiment(ticker, limit=limit)
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{ticker}/predict", response_model=DirectionPrediction)
def get_direction_prediction(ticker: str):
    try:
        return predict_direction(ticker)
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))