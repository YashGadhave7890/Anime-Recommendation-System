# ANIMORA — Backend API Documentation

The **ANIMORA REST API** is a high-performance FastAPI service connected to a SQLite database and the Phase 2 machine learning recommendation engine. It serves anime catalog queries, user interaction tracking (ratings, watchlist, watch history, preferences), and real-time personalized/hybrid recommendations.

---

## 1. Architecture & Design Principles

```
                       [ React Client / Frontend ]
                                   │
                              HTTP / REST
                                   ▼
                   ┌───────────────────────────────┐
                   │       FastAPI Application     │
                   │    (CORS, Schemas, Routers)   │
                   └───────────────┬───────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
       ┌────────────────────────┐      ┌────────────────────────┐
       │   SQLAlchemy 2.0 ORM   │      │  ML Recommendation Svc │
       │  (SQLite: animora.db)  │      │  (TF-IDF, Rocchio, WR) │
       ├────────────────────────┤      ├────────────────────────┤
       │ • anime_references     │      │ • content_recommender  │
       │ • users                │      │ • user_profile         │
       │ • ratings              │      │ • popularity_baseline  │
       │ • watchlist            │      │ • hybrid_engine        │
       │ • watch_history        │      │ • cold_start_handler   │
       │ • user_preferences     │      │ • precomputed models   │
       └────────────────────────┘      └────────────────────────┘
```

* **Framework**: FastAPI with asynchronous lifespan management.
* **Database**: SQLite with SQLAlchemy 2.0 (`data/animora.db`).
* **Validation**: Pydantic v2 schemas for all requests and responses.
* **Authentication**: Lightweight local/demo user mechanism via `X-User-Id` header or `user_id` query parameter (defaults to `demo_user`, ID: 1).
* **Startup Performance**: Pre-warmed ML singleton loads in `<150ms`.

---

## 2. Starting the Backend Server

```bash
# Start FastAPI with Uvicorn development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

* **Interactive OpenAPI Explorer (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 3. Database Schema

The database is automatically initialized and seeded on first startup (`data/animora.db`):

| Table | Primary Key | Key Columns | Description |
|---|---|---|---|
| `anime_references` | `mal_id` | `name`, `score`, `weighted_score`, `genres`, `type`, `episodes`, `members`, `release_year`, `img_url` | 17,495 anime catalog titles |
| `users` | `id` | `username`, `display_name`, `created_at` | Local/demo user accounts |
| `ratings` | `id` | `user_id`, `anime_id`, `rating` (1–10), `review`, `updated_at` | User ratings (UQ: `user_id, anime_id`) |
| `watchlist` | `id` | `user_id`, `anime_id`, `status` (`plan_to_watch`, `watching`, `completed`, `dropped`) | User watchlist (UQ: `user_id, anime_id`) |
| `watch_history` | `id` | `user_id`, `anime_id`, `progress_episodes`, `watched_at` | Viewing progress logs |
| `user_preferences`| `id` | `user_id` (UQ), `preferred_genres`, `preferred_types`, `updated_at` | User genre & format preferences |

---

## 4. Endpoints Specification & Examples

### A. Health & System Status

#### `GET /health`
Returns system operational status, database connection, and ML engine readiness.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ml_engine": "loaded",
  "records_loaded": 17495
}
```

---

### B. Anime Catalog

#### `GET /api/anime`
Paginated catalog with multi-dimensional filtering and sorting.

* **Query Parameters**:
  * `page` (int, default: 1): Page number
  * `limit` (int, default: 20, max: 100): Items per page
  * `genre` (str, optional): Filter by genre (e.g. `Action`, `Psychological`)
  * `type` (str, optional): Filter by format (`TV`, `Movie`, `OVA`, etc.)
  * `min_score` (float, optional): Minimum rating score (1.0 - 10.0)
  * `min_year` (int, optional): Earliest release year
  * `max_year` (int, optional): Latest release year
  * `sort_by` (str, default: `weighted_score`): `weighted_score`, `score`, `members`, `name`, `release_year`
  * `order` (str, default: `desc`): `asc` or `desc`

**Response `200 OK`**:
```json
{
  "items": [
    {
      "mal_id": 5114,
      "name": "Fullmetal Alchemist: Brotherhood",
      "english_name": "Fullmetal Alchemist: Brotherhood",
      "japanese_name": "鋼の錬金術師 FULLMETAL ALCHEMIST",
      "score": 9.17,
      "weighted_score": 9.12,
      "genres": "Action, Military, Adventure, Comedy, Drama, Magic, Fantasy, Shounen",
      "type": "TV",
      "episodes": 64,
      "members": 2248456,
      "release_year": 2009,
      "img_url": "https://cdn.myanimelist.net/images/anime/1223/96541.jpg"
    }
  ],
  "total": 17495,
  "page": 1,
  "limit": 20,
  "total_pages": 875
}
```

#### `GET /api/anime/{id}`
Retrieves complete anime details by MAL ID, including full plot synopsis.

**Response `200 OK`**:
```json
{
  "mal_id": 1535,
  "name": "Death Note",
  "english_name": "Death Note",
  "japanese_name": "デスノート",
  "score": 8.63,
  "weighted_score": 8.59,
  "genres": "Mystery, Police, Psychological, Supernatural, Thriller, Shounen",
  "type": "TV",
  "episodes": 37,
  "members": 2589507,
  "release_year": 2006,
  "synopsis": "A high school student discovers a supernatural notebook that grants him the ability to kill anyone...",
  "img_url": "https://cdn.myanimelist.net/images/anime/9/9453.jpg"
}
```

#### `GET /api/anime/search`
Prefix, substring, and fuzzy matching over romaji and English titles.

* **Query Parameters**:
  * `q` (str, required): Search query (e.g. `hunter x hunter`, `attack on titan`)
  * `limit` (int, default: 10): Maximum results

**Response `200 OK`**:
```json
[
  {
    "mal_id": 11061,
    "name": "Hunter x Hunter (2011)",
    "english_name": "Hunter x Hunter",
    "genres": "Action, Adventure, Fantasy, Shounen, Super Power",
    "type": "TV",
    "score": 9.1,
    "weighted_score": 9.02,
    "members": 1673924,
    "release_year": 2011,
    "img_url": "https://cdn.myanimelist.net/images/anime/1337/99013.jpg"
  }
]
```

#### `GET /api/anime/{id}/similar`
Returns content-based similar anime using TF-IDF cosine similarity.

* **Query Parameters**:
  * `top_n` (int, default: 10): Number of recommendations

**Response `200 OK`**:
```json
{
  "strategy": "content_based",
  "total": 5,
  "query_title": "Death Note",
  "recommendations": [
    {
      "rank": 1,
      "mal_id": 2994,
      "name": "Death Note: Rewrite",
      "genres": "Mystery, Police, Psychological, Supernatural, Thriller, Shounen",
      "type": "Special",
      "score": 7.7,
      "similarity_score": 0.3653,
      "img_url": "https://cdn.myanimelist.net/images/anime/12/8664.jpg"
    }
  ]
}
```

---

### C. Recommendations

#### `GET /api/recommendations/popular`
Returns non-personalized recommendations based on Bayesian weighted scores and popularity.

* **Query Parameters**: `genre`, `type`, `min_year`, `max_year`, `top_n`

#### `GET /api/recommendations/personalized`
Returns personalized recommendations for the authenticated user.

* **Query Parameters**:
  * `query_anime` (int, optional): MAL ID of currently viewed anime (item + user hybrid mode)
  * `type` (str, optional): Format filter
  * `top_n` (int, default: 10): Number of results
  * `w_content`, `w_user`, `w_pop` (float, optional): Custom linear weights
* **Headers**: `X-User-Id` (optional, default: `1`)

**Response `200 OK`**:
```json
{
  "strategy": "personalized",
  "total": 5,
  "user_id": 1,
  "weights_used": {
    "content": 0.0,
    "user": 0.7,
    "popularity": 0.3
  },
  "recommendations": [
    {
      "rank": 1,
      "mal_id": 121,
      "name": "Fullmetal Alchemist",
      "genres": "Action, Adventure, Comedy, Drama, Fantasy, Magic, Military, Shounen",
      "type": "TV",
      "score": 8.17,
      "user_score": 0.3361,
      "popularity_score": 0.8412,
      "hybrid_score": 0.4876
    }
  ]
}
```

---

### D. User Interactions (Ratings, Watchlist, History, Preferences)

#### `POST /api/ratings`
Submits or updates a rating (1.0 to 10.0) and optional review. Immediately updates future personalized recommendations.

* **Request Body**:
```json
{
  "anime_id": 1,
  "rating": 9.5,
  "review": "Timeless space western masterpiece with legendary music."
}
```

#### `GET /api/ratings`
Lists all ratings by the current user.

#### `POST /api/watchlist`
Adds an anime to the user's watchlist or updates status (`plan_to_watch`, `watching`, `completed`, `dropped`).

* **Request Body**:
```json
{
  "anime_id": 1575,
  "status": "watching"
}
```

#### `DELETE /api/watchlist/{id}`
Removes an anime from the user's watchlist by anime MAL ID. Returns `204 No Content`.

#### `GET /api/watchlist`
Lists the user's watchlist. Supports filtering by `?status=watching`.

#### `POST /api/history`
Logs episode viewing progress.

* **Request Body**:
```json
{
  "anime_id": 1535,
  "progress_episodes": 12
}
```

#### `POST /api/preferences`
Sets preferred genres and production formats.

* **Request Body**:
```json
{
  "preferred_genres": ["Psychological", "Sci-Fi", "Mystery"],
  "preferred_types": ["TV", "Movie"]
}
```

#### `GET /api/preferences`
Retrieves current user's preference record.

---

## 5. Recommendation Flow: API $\to$ ML Engine

```
1. Client makes GET /api/recommendations/personalized (with X-User-Id header)
                            │
2. Backend queries user interactions from SQLite:
   • Ratings table (liked titles >= 7.0, disliked titles <= 5.0)
   • Preferences table (preferred_genres, preferred_types)
                            │
3. Decision Logic:
   ┌───────────────────────┬──────────────────────────────────────────┐
   │ Condition             │ Engine Action                            │
   ├───────────────────────┼──────────────────────────────────────────┤
   │ User has ratings      │ • Builds Rocchio user vector             │
   │                       │ • Blends with content / popularity       │
   │                       │ • Excludes seen anime                    │
   │                       │ • Returns personalized hybrid ranking    │
   ├───────────────────────┼──────────────────────────────────────────┤
   │ User has NO ratings,  │ • Triggers Tier 1 Cold-Start             │
   │ but set genres        │ • Ranks genre overlap + Bayesian quality │
   ├───────────────────────┼──────────────────────────────────────────┤
   │ User has zero history │ • Triggers Tier 2 Cold-Start             │
   │ & zero preferences    │ • Returns diverse Bayesian baseline      │
   └───────────────────────┴──────────────────────────────────────────┘
                            │
4. Results serialized into Pydantic RecommendationResponse and returned to client
```

---

## 6. Running API Verification & Unit Tests

```bash
# Run all automated tests (Phases 1, 2, and 3: 51 tests)
pytest -v
```
