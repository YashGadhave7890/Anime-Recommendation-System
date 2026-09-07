"""
Watchlist router for managing anime bookmark status.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db
from backend.app.models.user import User
from backend.app.schemas.anime import AnimeSummary
from backend.app.schemas.interactions import WatchlistCreate, WatchlistResponse
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])
user_service = UserService()


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED, summary="Add or Update Watchlist Item")
def add_to_watchlist(
    payload: WatchlistCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds an anime to the user's watchlist or updates its status."""
    try:
        item = user_service.add_or_update_watchlist(
            db=db,
            user_id=user.id,
            anime_id=payload.anime_id,
            status_val=payload.status,
        )
        return WatchlistResponse(
            id=item.id,
            user_id=item.user_id,
            anime_id=item.anime_id,
            status=item.status,
            created_at=item.created_at,
            anime=AnimeSummary.model_validate(item.anime) if item.anime else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[WatchlistResponse], summary="Get User Watchlist")
def get_user_watchlist(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. 'plan_to_watch', 'watching')."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all watchlist items for the current user."""
    items = user_service.get_user_watchlist(db=db, user_id=user.id, status_filter=status_filter)
    return [
        WatchlistResponse(
            id=item.id,
            user_id=item.user_id,
            anime_id=item.anime_id,
            status=item.status,
            created_at=item.created_at,
            anime=AnimeSummary.model_validate(item.anime) if item.anime else None,
        )
        for item in items
    ]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove Anime from Watchlist")
def remove_from_watchlist(
    id: int = Path(..., description="Anime MyAnimeList ID to remove."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes an anime from the user's watchlist."""
    removed = user_service.remove_from_watchlist(db=db, user_id=user.id, anime_id=id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anime {id} not found in user's watchlist.",
        )
    return None
