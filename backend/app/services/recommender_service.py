"""
Bridge service connecting FastAPI endpoints with the ML Recommendation Engine.
Maintains a warm singleton instance of ml.recommendation_service.RecommendationService.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.interactions import Rating, UserPreference, WatchlistItem
from ml.recommendation_service import RecommendationService
from ml.utils import setup_logger

logger = setup_logger("APIRecommenderBridge")

_recommender_instance: Optional[RecommendationService] = None


def get_recommender() -> RecommendationService:
    """Retrieves or initializes the global RecommendationService singleton."""
    global _recommender_instance
    if _recommender_instance is None:
        logger.info("Warming up ML RecommendationService singleton for API...")
        _recommender_instance = RecommendationService(auto_train=True)
    return _recommender_instance


class RecommenderBridgeService:
    """High-level service connecting DB user interactions to ML models."""

    def __init__(self):
        self.ml_service = get_recommender()

    def get_similar_anime(self, anime_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """Content-based recommendations for an anime by MAL ID."""
        return self.ml_service.get_content_recommendations(query=anime_id, top_n=top_n)

    def get_popular(
        self,
        genre: Optional[str] = None,
        anime_type: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """Popularity and Bayesian quality baseline recommendations."""
        return self.ml_service.get_popular_recommendations(
            genre=genre,
            anime_type=anime_type,
            min_year=min_year,
            max_year=max_year,
            top_n=top_n,
        )

    def get_personalized(
        self,
        user_id: int,
        db: Session,
        query_anime: Optional[int] = None,
        weights: Optional[Dict[str, float]] = None,
        anime_type: Optional[str] = None,
        top_n: int = 10,
    ) -> Dict[str, Any]:
        """
        Generates personalized recommendations:
        - If user has rated anime -> Hybrid / User Profile Model
        - If user has no ratings but set preferred genres -> Cold-Start Tier 1
        - If user has no history or preferences -> Cold-Start Tier 2 (Diverse Quality)
        - Automatically excludes already rated and watched/watching anime titles.
        """
        # 1. Fetch user ratings from DB
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        
        # 2. Fetch user watchlist items marked as watching/completed to exclude
        watchlist_items = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == user_id,
            WatchlistItem.status.in_(["watching", "completed", "dropped"])
        ).all()
        exclude_ids = [w.anime_id for w in watchlist_items]

        # 3. Fetch user preferences from DB
        user_pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        preferred_genres = []
        if user_pref and user_pref.preferred_genres:
            preferred_genres = [g.strip() for g in user_pref.preferred_genres.split(",") if g.strip()]

        # Case A: User has ratings
        if user_ratings:
            history = [{"mal_id": r.anime_id, "rating": float(r.rating)} for r in user_ratings]
            recs = self.ml_service.get_hybrid_recommendations(
                query_anime=query_anime,
                user_history=history,
                weights=weights,
                anime_type=anime_type,
                top_n=top_n,
                exclude_ids=exclude_ids,
            )
            strategy = "hybrid" if query_anime else "personalized"
            return {
                "strategy": strategy,
                "total": len(recs),
                "user_id": user_id,
                "weights_used": recs[0].get("weights_used") if recs else None,
                "recommendations": recs,
            }

        # Case B: User has NO ratings, but provided preferred genres
        if preferred_genres:
            raw_recs = self.ml_service.get_cold_start_recommendations(
                selected_genres=preferred_genres,
                anime_type=anime_type,
                top_n=top_n + len(exclude_ids),
            )
            recs = [r for r in raw_recs if r["mal_id"] not in exclude_ids][:top_n]
            return {
                "strategy": "cold_start_genre_conditioned",
                "total": len(recs),
                "user_id": user_id,
                "recommendations": recs,
            }

        # Case C: Pure cold start (Zero interaction history)
        raw_recs = self.ml_service.get_cold_start_recommendations(
            selected_genres=None,
            anime_type=anime_type,
            top_n=top_n + len(exclude_ids),
        )
        recs = [r for r in raw_recs if r["mal_id"] not in exclude_ids][:top_n]
        return {
            "strategy": "cold_start_global_diverse",
            "total": len(recs),
            "user_id": user_id,
            "recommendations": recs,
        }

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fast title search using the precomputed ML index."""
        return self.ml_service.search_anime(query=query, limit=limit)
