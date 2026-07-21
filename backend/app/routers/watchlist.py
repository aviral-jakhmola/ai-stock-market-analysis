from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistItem
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/watchlist",
    tags=["Watchlist"],
)


@router.get("", response_model=list[WatchlistItem])
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the current user's full watchlist.
    """
    return db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()


@router.post("", response_model=WatchlistItem)
def add_to_watchlist(
    item: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adds a ticker to the current user's watchlist.
    Rejects duplicates (same user + ticker) via the DB's unique constraint.
    """
    ticker = item.ticker.upper()

    new_item = Watchlist(user_id=current_user.id, ticker=ticker)
    db.add(new_item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ticker} is already in your watchlist",
        )

    db.refresh(new_item)
    return new_item


@router.delete("/{item_id}")
def remove_from_watchlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Removes a watchlist entry — only if it belongs to the current user.
    """
    item = db.query(Watchlist).filter(
        Watchlist.id == item_id,
        Watchlist.user_id == current_user.id,
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()
    return {"detail": "Removed from watchlist"}