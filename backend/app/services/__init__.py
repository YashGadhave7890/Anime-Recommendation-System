"""
Services package exports.
"""

from backend.app.services.anime_service import AnimeService
from backend.app.services.recommender_service import RecommenderBridgeService, get_recommender
from backend.app.services.user_service import UserService

__all__ = [
    "AnimeService",
    "RecommenderBridgeService",
    "UserService",
    "get_recommender",
]
