"""
SQLAlchemy model for user profiles.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base


class User(Base):
    """
    User account model. Supports lightweight local/demo profiles.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False, default="Anime Fan")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    history_items = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")
    preference = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
