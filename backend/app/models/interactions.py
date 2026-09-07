"""
SQLAlchemy models for user interactions: ratings, watchlist, watch history, and preferences.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.database import Base


class Rating(Base):
    """User rating and review for an anime title."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("anime_references.mal_id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 to 10.0 scale
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "anime_id", name="uq_user_anime_rating"),
    )

    # Relationships
    user = relationship("User", back_populates="ratings")
    anime = relationship("AnimeReference", back_populates="ratings")


class WatchlistItem(Base):
    """Watchlist bookmark tracking."""

    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("anime_references.mal_id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="plan_to_watch")  # plan_to_watch, watching, completed, dropped
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "anime_id", name="uq_user_anime_watchlist"),
    )

    user = relationship("User", back_populates="watchlist_items")
    anime = relationship("AnimeReference", back_populates="watchlist_items")


class WatchHistory(Base):
    """Episode progress and watch history logging."""

    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("anime_references.mal_id", ondelete="CASCADE"), nullable=False, index=True)
    progress_episodes = Column(Integer, nullable=False, default=1)
    watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="history_items")
    anime = relationship("AnimeReference", back_populates="history_items")


class UserPreference(Base):
    """Declared taste preferences (genres and production formats)."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_genres = Column(Text, nullable=False, default="")  # Stored as comma-separated or JSON string
    preferred_types = Column(Text, nullable=False, default="")   # Stored as comma-separated or JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="preference")
