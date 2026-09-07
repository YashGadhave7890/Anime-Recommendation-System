"""
Health check router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.dependencies.db import get_db
from backend.app.models.anime import AnimeReference
from backend.app.schemas.common import HealthCheckResponse
from backend.app.services.recommender_service import get_recommender

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse, summary="System Health & Status")
def health_check(db: Session = Depends(get_db)):
    """
    Returns server operational status, database connection state,
    and ML recommendation engine readiness.
    """
    # 1. Check DB connectivity & catalog count
    db_status = "connected"
    record_count = 0
    try:
        record_count = db.query(AnimeReference).count()
    except Exception:
        db_status = "error"

    # 2. Check ML engine state
    ml_status = "loaded"
    try:
        recommender = get_recommender()
        if len(recommender.anime_df) == 0:
            ml_status = "empty"
    except Exception:
        ml_status = "error"

    overall_status = "healthy" if db_status == "connected" and ml_status == "loaded" else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        version=settings.VERSION,
        database=db_status,
        ml_engine=ml_status,
        records_loaded=record_count,
    )
