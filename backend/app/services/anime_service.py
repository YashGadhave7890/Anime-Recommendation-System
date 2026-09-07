"""
Service handling anime catalog database queries, filtering, sorting, and pagination.
"""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from backend.app.models.anime import AnimeReference
from backend.app.services.recommender_service import RecommenderBridgeService


class AnimeService:
    """Provides anime catalog access and filtering."""

    def __init__(self):
        self.recommender_bridge = RecommenderBridgeService()

    def get_by_id(self, db: Session, mal_id: int) -> Optional[AnimeReference]:
        """Retrieves a single anime by its unique MyAnimeList ID."""
        return db.query(AnimeReference).filter(AnimeReference.mal_id == mal_id).first()

    def list_anime(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        genre: Optional[str] = None,
        anime_type: Optional[str] = None,
        min_score: Optional[float] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        sort_by: str = "weighted_score",
        order: str = "desc",
    ) -> Tuple[List[AnimeReference], int]:
        """
        Retrieves a paginated list of anime matching given filter criteria.
        
        Returns:
            Tuple of (list_of_anime, total_count)
        """
        query = db.query(AnimeReference)

        # Filters
        if genre and genre.strip():
            # Match genre substring (case-insensitive in SQLite)
            query = query.filter(AnimeReference.genres.ilike(f"%{genre.strip()}%"))

        if anime_type and anime_type.strip().lower() != "all":
            query = query.filter(AnimeReference.type.ilike(anime_type.strip()))

        if min_score is not None:
            query = query.filter(AnimeReference.score >= min_score)

        if min_year is not None:
            query = query.filter(AnimeReference.release_year >= min_year)

        if max_year is not None:
            query = query.filter(AnimeReference.release_year <= max_year)

        # Total count before pagination
        total_count = query.count()

        # Sorting
        valid_sort_fields = {
            "weighted_score": AnimeReference.weighted_score,
            "score": AnimeReference.score,
            "members": AnimeReference.members,
            "name": AnimeReference.name,
            "release_year": AnimeReference.release_year,
        }
        sort_column = valid_sort_fields.get(sort_by, AnimeReference.weighted_score)
        direction = desc if order.lower() == "desc" else asc
        query = query.order_by(direction(sort_column))

        # Pagination
        offset = max(0, (page - 1) * limit)
        items = query.offset(offset).limit(limit).all()

        return items, total_count

    def search_anime(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Delegates fast fuzzy & prefix search to precomputed index."""
        return self.recommender_bridge.search(query=query, limit=limit)
