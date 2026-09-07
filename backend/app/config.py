"""
Backend configuration settings using Pydantic.
Provides platform-independent path resolution and environment-based overrides.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Project Root Directory (derived relative to this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_PARQUET_PATH = DATA_DIR / "processed" / "cleaned_anime.parquet"
DEFAULT_SQLITE_PATH = DATA_DIR / "animora.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _parse_cors_origins() -> List[str]:
    """Parses CORS origins from environment variable with development fallbacks."""
    env_origins = os.getenv("CORS_ORIGINS")
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    if not env_origins:
        return default_origins

    parsed = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return parsed if parsed else default_origins


def _resolve_database_url() -> str:
    """Resolves database URL, ensuring SQLite paths are absolute and parent directories exist."""
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

    if raw_url.startswith("sqlite:///"):
        sqlite_file_path = raw_url.replace("sqlite:///", "")
        if sqlite_file_path and not sqlite_file_path.startswith(":memory:"):
            target_path = Path(sqlite_file_path)
            if not target_path.is_absolute():
                target_path = (BASE_DIR / target_path).resolve()
            # Ensure SQLite target directory exists on disk (e.g. Render persistent mount)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{target_path.as_posix()}"

    return raw_url


class Settings(BaseModel):
    """Application configuration settings."""

    PROJECT_NAME: str = "ANIMORA — Anime Recommendation Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = "Production-grade REST API for ANIMORA personalized anime recommendations."

    # Server Configuration (Supports hosting platform $PORT e.g. Render)
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database Configuration (Resolves SQLite or PostgreSQL)
    DATABASE_URL: str = _resolve_database_url()

    # CORS Configuration for Frontend (supports comma-separated env var)
    CORS_ORIGINS: List[str] = _parse_cors_origins()

    # Demo User Constants
    DEFAULT_USER_ID: int = 1
    DEFAULT_USERNAME: str = "demo_user"
    DEFAULT_DISPLAY_NAME: str = "Anime Fan"

    # Recommendation defaults
    DEFAULT_REC_LIMIT: int = 10
    MAX_REC_LIMIT: int = 50


settings = Settings()
