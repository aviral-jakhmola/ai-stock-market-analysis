from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.search_history import SearchHistory
from app.models.user import User
from app.schemas.search_history import (
    SearchHistoryCreate,
    SearchHistoryResponse,
)

router = APIRouter(
    prefix="/api/search-history",
    tags=["Search History"],
)


@router.post("", response_model=SearchHistoryResponse)
def log_search(
    data: SearchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.user_id == current_user.id,
            SearchHistory.ticker == data.ticker,
        )
        .first()
    )

    if existing:
        existing.searched_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    history = SearchHistory(
        user_id=current_user.id,
        ticker=data.ticker,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


@router.get("", response_model=list[SearchHistoryResponse])
def get_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.searched_at.desc(), SearchHistory.id.desc())
        .limit(10)
        .all()
    )