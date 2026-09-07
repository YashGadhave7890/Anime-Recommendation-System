"""
Watch history router for logging episode progress.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db
from backend.app.models.user import User
from backend.app.schemas.anime import AnimeSummary
from backend.app.schemas.interactions import WatchHistoryCreate, WatchHistoryResponse
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/history", tags=["Watch History"])
user_service = UserService()


@router.post("", response_model=WatchHistoryResponse, status_code=status.HTTP_201_CREATED, summary="Log Watch Progress")
def log_watch_history(
    payload: WatchHistoryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Records an episode viewing progress entry."""
    try:
        record = user_service.log_watch_history(
            db=db,
            user_id=user.id,
            anime_id=payload.anime_id,
            progress_episodes=payload.progress_episodes,
        )
        return WatchHistoryResponse(
            id=record.id,
            user_id=record.user_id,
            anime_id=record.anime_id,
            progress_episodes=record.progress_episodes,
            watched_at=record.watched_at,
            anime=AnimeSummary.model_validate(record.anime) if record.anime else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[WatchHistoryResponse], summary="Get Watch History")
def get_user_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all watch history entries for the current user."""
    history = user_service.get_user_history(db=db, user_id=user.id)
    return [
        WatchHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            anime_id=h.anime_id,
            progress_episodes=h.progress_episodes,
            watched_at=h.watched_at,
            anime=AnimeSummary.model_validate(h.anime) if h.anime else None,
        )
        for h in history
    ]
