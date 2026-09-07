"""
Routers package exports.
"""

from backend.app.routers.anime import router as anime_router
from backend.app.routers.health import router as health_router
from backend.app.routers.history import router as history_router
from backend.app.routers.preferences import router as preferences_router
from backend.app.routers.ratings import router as ratings_router
from backend.app.routers.recommendations import router as recommendations_router
from backend.app.routers.watchlist import router as watchlist_router

__all__ = [
    "health_router",
    "anime_router",
    "recommendations_router",
    "ratings_router",
    "watchlist_router",
    "history_router",
    "preferences_router",
]
