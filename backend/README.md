# ANIMORA — FastAPI Backend Service

The high-performance REST API backend for **ANIMORA — Personalized Anime Recommendation Engine**, built with **FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite / PostgreSQL, and Uvicorn**.

---

## 1. Architecture & Overview

The backend acts as the service layer between the ML recommendation engine (`ml/`) and the React frontend (`frontend/`). It encapsulates data persistence, user interaction logging, catalog querying, and serves personalized recommendations through high-performance async endpoints.

- **Framework**: FastAPI (asynchronous, auto-generating OpenAPI documentation)
- **Data Layer**: SQLAlchemy 2.0 ORM over SQLite (`data/animora.db`) with PostgreSQL compatibility
- **ML Integration**: In-memory `RecommendationService` singleton loaded once during application startup (`lifespan`), executing sparse vector dot products in ~5 ms
- **CORS**: Dynamically configured via `CORS_ORIGINS` environment variable
- **Validation**: Strict Pydantic v2 schemas for request validation and response serialization

---

## 2. Directory Structure

```
backend/app/
├── main.py                  # Application entry point, lifespan, CORS, router mounting
├── config.py                # Pydantic Settings & environment variable resolution
├── database.py              # SQLAlchemy engine, sessionmaker, and Base declarative model
├── seed.py                  # Database seeder (17,495 anime titles + demo user personas)
├── dependencies/
│   ├── auth.py              # X-User-Id header resolver (Demo user 1 vs Cold-start user 2)
│   └── db.py                # SQLAlchemy session lifecycle dependency (get_db)
├── models/
│   ├── anime.py             # AnimeReference table definition (17,495 rows)
│   ├── interactions.py      # Rating, WatchlistItem, WatchHistory tables
│   └── user.py              # User and UserPreference tables
├── schemas/
│   ├── anime.py             # AnimeResponse, AnimeListResponse, Filter schemas
│   ├── interactions.py      # RatingCreate, WatchlistCreate, Preferences schemas
│   ├── recommendations.py   # RecommendationResponse and RecommendationItem schemas
│   └── common.py            # Pagination and message schemas
├── services/
│   ├── anime_service.py     # Catalog querying, filtering, search, pagination
│   ├── user_service.py      # Ratings CRUD, watchlist management, preference updates
│   └── recommender_service.py # Bridge service connecting API routers to ml.RecommendationService
└── routers/
    ├── health.py            # /health (System status, DB check, ML readiness)
    ├── anime.py             # /api/anime (Catalog, details, search autocomplete, similar)
    ├── recommendations.py   # /api/recommendations (Personalized, popular, hybrid)
    ├── ratings.py           # /api/ratings (User ratings CRUD)
    ├── watchlist.py         # /api/watchlist (Bookmark management)
    ├── history.py           # /api/history (Viewing progress logs)
    └── preferences.py       # /api/preferences (Cold-start taste preference tuning)
```

---

## 3. Core API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check reporting DB connectivity and loaded catalog count |
| `GET` | `/api/anime` | Paginated catalog with multi-attribute filtering (genre, format, score, year) |
| `GET` | `/api/anime/{id}` | Detailed anime metadata, synopsis, and Bayesian score |
| `GET` | `/api/anime/search` | Fast prefix and fuzzy title auto-complete |
| `GET` | `/api/anime/{id}/similar` | Content-based recommendations using TF-IDF cosine similarity |
| `GET` | `/api/recommendations/personalized` | Hybrid Rocchio user-profile recommendations with adjustable weights |
| `GET` | `/api/recommendations/popular` | Bayesian weighted score and popularity baseline recommendations |
| `POST` | `/api/ratings` | Submit or update user star rating (1.0–10.0) with review text |
| `GET` | `/api/ratings` | Retrieve ratings for the active user persona |
| `POST` | `/api/watchlist` | Add anime to watchlist (`plan_to_watch`, `watching`, `completed`, `dropped`) |
| `GET` | `/api/watchlist` | Retrieve user's watchlist |
| `DELETE` | `/api/watchlist/{id}` | Remove anime from watchlist |
| `GET` | `/api/preferences` | Retrieve user cold-start genre and format preferences |
| `POST` | `/api/preferences` | Update user genre and format preferences |

Interactive Swagger documentation is available at `http://localhost:8000/docs` when running locally.

---

## 4. Local Execution & Database Seeding

```bash
# Seed the database from cleaned parquet catalog (takes ~3s)
python -m backend.app.seed

# Start the development server with auto-reload
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
