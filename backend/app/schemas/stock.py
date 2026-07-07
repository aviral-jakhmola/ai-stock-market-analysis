from pydantic import BaseModel
from datetime import datetime


class StockHistory(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int