"""
SQLAlchemy model for anime catalog reference data.
"""

from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base


class AnimeReference(Base):
    """
    Reference metadata model for anime titles in the ANIMORA catalog.
    Provides fast indexed SQL queries, joins, and relationships.
    """

    __tablename__ = "anime_references"

    mal_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    english_name = Column(String(255), nullable=True)
    japanese_name = Column(String(255), nullable=True)
    score = Column(Float, nullable=True)
    weighted_score = Column(Float, index=True, default=0.0)
    genres = Column(String(500), index=True, default="")
    type = Column(String(50), index=True, default="Unknown")
    episodes = Column(Float, nullable=True)
    members = Column(Integer, index=True, default=0)
    release_year = Column(Integer, index=True, nullable=True)
    synopsis = Column(Text, nullable=True)
    img_url = Column(String(500), nullable=True)

    # Relationships to user interactions
    ratings = relationship("Rating", back_populates="anime", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="anime", cascade="all, delete-orphan")
    history_items = relationship("WatchHistory", back_populates="anime", cascade="all, delete-orphan")
