from datetime import datetime
from pydantic import BaseModel


class SearchHistoryCreate(BaseModel):
    ticker: str


class SearchHistoryResponse(BaseModel):
    id: int
    ticker: str
    searched_at: datetime

    class Config:
        from_attributes = True