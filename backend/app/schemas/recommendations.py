"""
Pydantic schemas for recommendation responses.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Schema for an individual recommended anime item."""
    rank: int
    mal_id: int
    name: str
    english_name: Optional[str] = None
    genres: str
    type: str
    score: Optional[float] = None
    weighted_score: Optional[float] = None
    members: Optional[int] = 0
    release_year: Optional[int] = None
    similarity_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    baseline_score: Optional[float] = None
    cold_score: Optional[float] = None
    img_url: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Container schema for recommendation list responses."""
    strategy: str = Field(..., description="Strategy used: 'content', 'personalized', 'hybrid', 'cold_start', 'popular'")
    total: int
    query_title: Optional[str] = None
    user_id: Optional[int] = None
    weights_used: Optional[Dict[str, float]] = None
    recommendations: List[RecommendationItem]
