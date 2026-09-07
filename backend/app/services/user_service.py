"""
Service managing user interactions: ratings, watchlist, watch history, and taste preferences.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from backend.app.models.anime import AnimeReference
from backend.app.models.interactions import (
    Rating,
    UserPreference,
    WatchHistory,
    WatchlistItem,
)


class UserService:
    """Handles CRUD operations for user interactions."""

    # -------------------------------------------------------------------------
    # Ratings
    # -------------------------------------------------------------------------

    def create_or_update_rating(
        self,
        db: Session,
        user_id: int,
        anime_id: int,
        rating_val: float,
        review: Optional[str] = None,
    ) -> Rating:
        """Creates a new rating or updates an existing rating for an anime."""
        # Verify anime exists
        anime = db.query(AnimeReference).filter(AnimeReference.mal_id == anime_id).first()
        if not anime:
            raise ValueError(f"Anime with ID {anime_id} does not exist in catalog.")

        existing = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.anime_id == anime_id,
        ).first()

        if existing:
            existing.rating = rating_val
            if review is not None:
                existing.review = review
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        new_rating = Rating(
            user_id=user_id,
            anime_id=anime_id,
            rating=rating_val,
            review=review,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating

    def get_user_ratings(self, db: Session, user_id: int) -> List[Rating]:
        """Retrieves all ratings by a user, including joined anime metadata."""
        return (
            db.query(Rating)
            .options(joinedload(Rating.anime))
            .filter(Rating.user_id == user_id)
            .order_by(Rating.created_at.desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Watchlist
    # -------------------------------------------------------------------------

    def add_or_update_watchlist(
        self,
        db: Session,
        user_id: int,
        anime_id: int,
        status_val: str = "plan_to_watch",
    ) -> WatchlistItem:
        """Adds or updates an anime in the user's watchlist."""
        anime = db.query(AnimeReference).filter(AnimeReference.mal_id == anime_id).first()
        if not anime:
            raise ValueError(f"Anime with ID {anime_id} does not exist in catalog.")

        existing = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == user_id,
            WatchlistItem.anime_id == anime_id,
        ).first()

        if existing:
            existing.status = status_val
            db.commit()
            db.refresh(existing)
            return existing

        item = WatchlistItem(
            user_id=user_id,
            anime_id=anime_id,
            status=status_val,
            created_at=datetime.utcnow(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def remove_from_watchlist(self, db: Session, user_id: int, anime_id: int) -> bool:
        """Removes an anime from the user's watchlist."""
        item = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == user_id,
            WatchlistItem.anime_id == anime_id,
        ).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False

    def get_user_watchlist(
        self,
        db: Session,
        user_id: int,
        status_filter: Optional[str] = None,
    ) -> List[WatchlistItem]:
        """Retrieves user's watchlist items with optional status filtering."""
        query = db.query(WatchlistItem).options(joinedload(WatchlistItem.anime)).filter(
            WatchlistItem.user_id == user_id
        )
        if status_filter and status_filter.strip().lower() != "all":
            query = query.filter(WatchlistItem.status.ilike(status_filter.strip()))
        return query.order_by(WatchlistItem.created_at.desc()).all()

    # -------------------------------------------------------------------------
    # Watch History
    # -------------------------------------------------------------------------

    def log_watch_history(
        self,
        db: Session,
        user_id: int,
        anime_id: int,
        progress_episodes: int = 1,
    ) -> WatchHistory:
        """Records an episode viewing event in watch history."""
        anime = db.query(AnimeReference).filter(AnimeReference.mal_id == anime_id).first()
        if not anime:
            raise ValueError(f"Anime with ID {anime_id} does not exist in catalog.")

        record = WatchHistory(
            user_id=user_id,
            anime_id=anime_id,
            progress_episodes=progress_episodes,
            watched_at=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_user_history(self, db: Session, user_id: int) -> List[WatchHistory]:
        """Retrieves user's watch history sorted by most recent first."""
        return (
            db.query(WatchHistory)
            .options(joinedload(WatchHistory.anime))
            .filter(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watched_at.desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # User Preferences
    # -------------------------------------------------------------------------

    def set_user_preferences(
        self,
        db: Session,
        user_id: int,
        preferred_genres: List[str],
        preferred_types: List[str],
    ) -> UserPreference:
        """Sets or updates preferred genres and formats for cold-start and hybrid tuning."""
        genres_str = ", ".join([g.strip() for g in preferred_genres if g.strip()])
        types_str = ", ".join([t.strip() for t in preferred_types if t.strip()])

        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if pref:
            pref.preferred_genres = genres_str
            pref.preferred_types = types_str
            pref.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(pref)
            return pref

        pref = UserPreference(
            user_id=user_id,
            preferred_genres=genres_str,
            preferred_types=types_str,
            updated_at=datetime.utcnow(),
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
        return pref

    def get_user_preferences(self, db: Session, user_id: int) -> Optional[UserPreference]:
        """Retrieves user's preference record."""
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
