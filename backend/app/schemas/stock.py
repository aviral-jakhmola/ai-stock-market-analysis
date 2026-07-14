from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockHistory(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None

    rsi_14: Optional[float] = None

class CompanyOverview(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    currency: Optional[str] = None

class NewsArticleSentiment(BaseModel):
    title: Optional[str] = None
    publisher: Optional[str] = None
    link: Optional[str] = None
    published: Optional[str] = None
    sentiment: dict


class SentimentSummary(BaseModel):
    ticker: str
    articles: list[NewsArticleSentiment]
    summary: dict
    overall_sentiment: str