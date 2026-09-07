"""
Pydantic schemas for anime catalog models.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnimeSummary(BaseModel):
    """Compact summary schema for cards, lists, and search results."""
    model_config = ConfigDict(from_attributes=True)

    mal_id: int
    name: str
    english_name: Optional[str] = None
    japanese_name: Optional[str] = None
    score: Optional[float] = None
    weighted_score: Optional[float] = None
    genres: str
    type: str
    episodes: Optional[float] = None
    members: int
    release_year: Optional[int] = None
    img_url: Optional[str] = None


class AnimeDetail(AnimeSummary):
    """Full detail schema for anime overview pages."""
    synopsis: Optional[str] = None
