from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


class SearchHistoryCreate(BaseModel):
    ticker: str


class SearchHistoryResponse(BaseModel):
    id: int
    ticker: str
    searched_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("searched_at")
    def serialize_searched_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.isoformat().replace("+00:00", "Z")