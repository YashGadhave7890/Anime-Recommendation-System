"""
Recommendation engine router: popular baseline and personalized/hybrid recommendations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db
from backend.app.models.user import User
from backend.app.schemas.recommendations import RecommendationResponse
from backend.app.services.recommender_service import RecommenderBridgeService

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])
recommender_bridge = RecommenderBridgeService()


@router.get("/popular", response_model=RecommendationResponse, summary="Popular & Bayesian Quality Baseline")
def get_popular_recommendations(
    genre: Optional[str] = Query(None, description="Optional genre filter."),
    type: Optional[str] = Query(None, description="Optional production format ('TV', 'Movie', etc.)."),
    min_year: Optional[int] = Query(None, ge=1900, description="Minimum release year."),
    max_year: Optional[int] = Query(None, le=2030, description="Maximum release year."),
    top_n: int = Query(10, ge=1, le=50, description="Number of items to recommend."),
    db: Session = Depends(get_db),
):
    """
    Returns non-personalized baseline recommendations based on Bayesian weighted scores
    and log-transformed community popularity.
    """
    recs = recommender_bridge.get_popular(
        genre=genre,
        anime_type=type,
        min_year=min_year,
        max_year=max_year,
        top_n=top_n,
    )
    return RecommendationResponse(
        strategy="popular_baseline",
        total=len(recs),
        recommendations=recs,
    )


@router.get("/personalized", response_model=RecommendationResponse, summary="Personalized & Hybrid Recommendations")
def get_personalized_recommendations(
    query_anime: Optional[int] = Query(None, description="Currently viewed anime MAL ID (for item+user hybrid mode)."),
    type: Optional[str] = Query(None, description="Production format filter (e.g. 'TV', 'Movie')."),
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations."),
    w_content: Optional[float] = Query(None, ge=0.0, le=1.0, description="Weight for content similarity."),
    w_user: Optional[float] = Query(None, ge=0.0, le=1.0, description="Weight for user taste profile."),
    w_pop: Optional[float] = Query(None, ge=0.0, le=1.0, description="Weight for popularity baseline."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates personalized recommendations for the current user:
    - If user has rated anime: Blends user taste profile, content similarity (if query anime provided), and popularity.
    - If user has no ratings but set preferred genres: Automatically triggers Tier 1 cold-start (genre-conditioned).
    - If user has no history or preferences: Automatically triggers Tier 2 cold-start (diverse global quality).
    """
    custom_weights = None
    if any(w is not None for w in [w_content, w_user, w_pop]):
        custom_weights = {
            "content": w_content or 0.0,
            "user": w_user or 0.0,
            "popularity": w_pop or 0.0,
        }

    res = recommender_bridge.get_personalized(
        user_id=user.id,
        db=db,
        query_anime=query_anime,
        weights=custom_weights,
        anime_type=type,
        top_n=top_n,
    )

    return RecommendationResponse(
        strategy=res["strategy"],
        total=res["total"],
        user_id=user.id,
        weights_used=res.get("weights_used"),
        recommendations=res["recommendations"],
    )
