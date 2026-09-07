"""
Database models package.
"""

from backend.app.models.anime import AnimeReference
from backend.app.models.interactions import (
    Rating,
    UserPreference,
    WatchHistory,
    WatchlistItem,
)
from backend.app.models.user import User

__all__ = [
    "AnimeReference",
    "User",
    "Rating",
    "WatchlistItem",
    "WatchHistory",
    "UserPreference",
]
