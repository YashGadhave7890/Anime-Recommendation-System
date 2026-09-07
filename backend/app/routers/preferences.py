"""
User genre and format preferences router.
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db
from backend.app.models.user import User
from backend.app.schemas.interactions import UserPreferenceCreate, UserPreferenceResponse
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/preferences", tags=["User Preferences"])
user_service = UserService()


@router.post("", response_model=UserPreferenceResponse, summary="Set User Preferences")
def set_user_preferences(
    payload: UserPreferenceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sets or updates the user's preferred genres and formats.
    Used for cold-start recommendations and hybrid tuning.
    """
    pref = user_service.set_user_preferences(
        db=db,
        user_id=user.id,
        preferred_genres=payload.preferred_genres,
        preferred_types=payload.preferred_types,
    )
    genres = [g.strip() for g in pref.preferred_genres.split(",") if g.strip()]
    types = [t.strip() for t in pref.preferred_types.split(",") if t.strip()]

    return UserPreferenceResponse(
        user_id=pref.user_id,
        preferred_genres=genres,
        preferred_types=types,
        updated_at=pref.updated_at,
    )


@router.get("", response_model=UserPreferenceResponse, summary="Get User Preferences")
def get_user_preferences(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves the current user's preferred genres and formats."""
    pref = user_service.get_user_preferences(db=db, user_id=user.id)
    if not pref:
        return UserPreferenceResponse(
            user_id=user.id,
            preferred_genres=[],
            preferred_types=[],
            updated_at=datetime.utcnow(),
        )

    genres = [g.strip() for g in pref.preferred_genres.split(",") if g.strip()]
    types = [t.strip() for t in pref.preferred_types.split(",") if t.strip()]

    return UserPreferenceResponse(
        user_id=pref.user_id,
        preferred_genres=genres,
        preferred_types=types,
        updated_at=pref.updated_at,
    )
