"""
Main FastAPI Application Entrypoint for ANIMORA.
Configures lifespan events, CORS middleware, API routers, and documentation.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import (
    anime_router,
    health_router,
    history_router,
    preferences_router,
    ratings_router,
    recommendations_router,
    watchlist_router,
)
from backend.app.seed import seed_database
from backend.app.services.recommender_service import get_recommender
from ml.utils import setup_logger

logger = setup_logger("APIApp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database tables, runs seed verification, and warms ML models on startup.
    """
    logger.info("Initializing ANIMORA API Backend...")
    # 1. Initialize tables & ensure catalog is seeded
    init_db()
    seed_database(force=False)

    # 2. Warm up ML Recommendation Engine singleton
    logger.info("Warming up ML Recommendation Engine...")
    get_recommender()

    logger.info("ANIMORA API Backend successfully initialized and ready!")
    yield
    logger.info("Shutting down ANIMORA API Backend...")


# FastAPI Application Factory
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware (Enables React / Vite clients on localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health_router)
app.include_router(anime_router)
app.include_router(recommendations_router)
app.include_router(ratings_router)
app.include_router(watchlist_router)
app.include_router(history_router)
app.include_router(preferences_router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming clients and directing to API documentation."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "message": "Welcome to ANIMORA Recommendation API! Visit /docs for interactive OpenAPI explorer.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development"),
    )
