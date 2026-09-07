"""
Anime catalog API router: browsing, detail, search, and content-based similarity.
"""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies.db import get_db
from backend.app.schemas.anime import AnimeDetail, AnimeSummary
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.recommendations import RecommendationResponse
from backend.app.services.anime_service import AnimeService

router = APIRouter(prefix="/api/anime", tags=["Anime Catalog"])
anime_service = AnimeService()


@router.get("", response_model=PaginatedResponse[AnimeSummary], summary="List & Filter Anime Catalog")
def get_anime_list(
    page: int = Query(1, ge=1, description="Page number."),
    limit: int = Query(20, ge=1, le=100, description="Items per page."),
    genre: Optional[str] = Query(None, description="Genre filter (e.g. 'Action', 'Psychological')."),
    type: Optional[str] = Query(None, description="Production type ('TV', 'Movie', 'OVA', etc.)."),
    min_score: Optional[float] = Query(None, ge=1.0, le=10.0, description="Minimum MAL score."),
    min_year: Optional[int] = Query(None, ge=1900, description="Earliest release year."),
    max_year: Optional[int] = Query(None, le=2030, description="Latest release year."),
    sort_by: str = Query("weighted_score", pattern="^(weighted_score|score|members|name|release_year)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """Retrieves paginated and filtered anime catalog records."""
    items, total = anime_service.list_anime(
        db=db,
        page=page,
        limit=limit,
        genre=genre,
        anime_type=type,
        min_score=min_score,
        min_year=min_year,
        max_year=max_year,
        sort_by=sort_by,
        order=order,
    )
    total_pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse[AnimeSummary](
        items=[AnimeSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/search", response_model=List[AnimeSummary], summary="Search Anime Titles")
def search_anime(
    q: str = Query(..., min_length=1, description="Title search term."),
    limit: int = Query(10, ge=1, le=50, description="Maximum results."),
    db: Session = Depends(get_db),
):
    """Searches anime titles using prefix, substring, and fuzzy matching."""
    results = anime_service.search_anime(query=q, limit=limit)
    return [AnimeSummary(**item) for item in results]


@router.get("/{id}", response_model=AnimeDetail, summary="Get Anime Details by ID")
def get_anime_detail(
    id: int = Path(..., ge=1, description="Anime MyAnimeList ID."),
    db: Session = Depends(get_db),
):
    """Retrieves full anime details including synopsis by MAL ID."""
    anime = anime_service.get_by_id(db=db, mal_id=id)
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anime with ID {id} not found.",
        )
    return AnimeDetail.model_validate(anime)


@router.get("/{id}/similar", response_model=RecommendationResponse, summary="Get Similar Anime (Content-Based)")
def get_similar_anime(
    id: int = Path(..., ge=1, description="Reference anime MyAnimeList ID."),
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations."),
    db: Session = Depends(get_db),
):
    """
    Returns content-based similar anime using TF-IDF cosine similarity over content soup.
    The input anime is strictly excluded from results.
    """
    anime = anime_service.get_by_id(db=db, mal_id=id)
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anime with ID {id} not found in catalog.",
        )

    try:
        recs = anime_service.recommender_bridge.get_similar_anime(anime_id=id, top_n=top_n)
        return RecommendationResponse(
            strategy="content_based",
            total=len(recs),
            query_title=anime.name,
            recommendations=recs,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
