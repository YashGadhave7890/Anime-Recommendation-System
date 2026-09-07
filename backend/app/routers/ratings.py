"""
Ratings router for submitting and retrieving user anime ratings.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db
from backend.app.models.user import User
from backend.app.schemas.anime import AnimeSummary
from backend.app.schemas.interactions import RatingCreate, RatingResponse
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/ratings", tags=["User Ratings"])
user_service = UserService()


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED, summary="Submit or Update Rating")
def submit_rating(
    payload: RatingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a rating (1.0 - 10.0) for an anime.
    If the user has already rated the title, updates the rating and review.
    Immediately influences future personalized recommendations.
    """
    try:
        rating_obj = user_service.create_or_update_rating(
            db=db,
            user_id=user.id,
            anime_id=payload.anime_id,
            rating_val=payload.rating,
            review=payload.review,
        )
        return RatingResponse(
            id=rating_obj.id,
            user_id=rating_obj.user_id,
            anime_id=rating_obj.anime_id,
            rating=rating_obj.rating,
            review=rating_obj.review,
            created_at=rating_obj.created_at,
            updated_at=rating_obj.updated_at,
            anime=AnimeSummary.model_validate(rating_obj.anime) if rating_obj.anime else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[RatingResponse], summary="Get User Ratings")
def get_user_ratings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all ratings submitted by the current user."""
    ratings = user_service.get_user_ratings(db=db, user_id=user.id)
    return [
        RatingResponse(
            id=r.id,
            user_id=r.user_id,
            anime_id=r.anime_id,
            rating=r.rating,
            review=r.review,
            created_at=r.created_at,
            updated_at=r.updated_at,
            anime=AnimeSummary.model_validate(r.anime) if r.anime else None,
        )
        for r in ratings
    ]
