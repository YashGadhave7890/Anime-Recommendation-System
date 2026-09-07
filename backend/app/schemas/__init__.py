"""
Schemas package exports.
"""

from backend.app.schemas.anime import AnimeDetail, AnimeSummary
from backend.app.schemas.common import HealthCheckResponse, MessageResponse, PaginatedResponse
from backend.app.schemas.interactions import (
    RatingCreate,
    RatingResponse,
    UserPreferenceCreate,
    UserPreferenceResponse,
    WatchHistoryCreate,
    WatchHistoryResponse,
    WatchlistCreate,
    WatchlistResponse,
)
from backend.app.schemas.recommendations import RecommendationItem, RecommendationResponse

__all__ = [
    "AnimeSummary",
    "AnimeDetail",
    "HealthCheckResponse",
    "MessageResponse",
    "PaginatedResponse",
    "RecommendationItem",
    "RecommendationResponse",
    "RatingCreate",
    "RatingResponse",
    "WatchlistCreate",
    "WatchlistResponse",
    "WatchHistoryCreate",
    "WatchHistoryResponse",
    "UserPreferenceCreate",
    "UserPreferenceResponse",
]
