"""
Pydantic schemas for user ratings, watchlist, watch history, and preferences.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.anime import AnimeSummary


# -----------------------------------------------------------------------------
# Ratings
# -----------------------------------------------------------------------------

class RatingCreate(BaseModel):
    anime_id: int = Field(..., description="MyAnimeList ID of the anime.")
    rating: float = Field(..., ge=1.0, le=10.0, description="Score rating from 1.0 to 10.0.")
    review: Optional[str] = Field(None, max_length=2000, description="Optional text review.")


class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    anime_id: int
    rating: float
    review: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    anime: Optional[AnimeSummary] = None


# -----------------------------------------------------------------------------
# Watchlist
# -----------------------------------------------------------------------------

class WatchlistCreate(BaseModel):
    anime_id: int = Field(..., description="MyAnimeList ID of the anime.")
    status: str = Field("plan_to_watch", description="Status: 'plan_to_watch', 'watching', 'completed', 'dropped'.")


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    anime_id: int
    status: str
    created_at: datetime
    anime: Optional[AnimeSummary] = None


# -----------------------------------------------------------------------------
# Watch History
# -----------------------------------------------------------------------------

class WatchHistoryCreate(BaseModel):
    anime_id: int = Field(..., description="MyAnimeList ID of the anime.")
    progress_episodes: int = Field(1, ge=1, description="Number of episodes watched.")


class WatchHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    anime_id: int
    progress_episodes: int
    watched_at: datetime
    anime: Optional[AnimeSummary] = None


# -----------------------------------------------------------------------------
# User Preferences
# -----------------------------------------------------------------------------

class UserPreferenceCreate(BaseModel):
    preferred_genres: List[str] = Field(default_factory=list, description="List of preferred genres.")
    preferred_types: List[str] = Field(default_factory=list, description="List of preferred formats (e.g. TV, Movie).")


class UserPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    preferred_genres: List[str]
    preferred_types: List[str]
    updated_at: datetime
