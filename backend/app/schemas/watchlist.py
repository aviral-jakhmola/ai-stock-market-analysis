from pydantic import BaseModel
from datetime import datetime


class WatchlistCreate(BaseModel):
    """
    What the frontend sends when adding a ticker to the watchlist.
    """
    ticker: str


class WatchlistItem(BaseModel):
    """
    A single watchlist entry, as returned to the frontend.
    """
    id: int
    ticker: str
    added_at: datetime

    class Config:
        from_attributes = True