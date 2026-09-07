# ANIMORA — Personalized Anime Recommendation Engine

> **Discover what you'll love next.**  
> A portfolio-grade, full-stack machine learning anime recommendation platform over 17,495 authentic MyAnimeList titles.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/Tests-51%20Passed-success?style=flat&logo=pytest&logoColor=white)](tests/)

---

## Demo / Screenshots

*Screenshots and UI walkthroughs can be embedded here.*

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [ANIMORA UI PREVIEW]                                                                   │
│                                                                                        │
│   ANIMORA  [Home] [Discover] [Recommendations] [Watchlist] [Profile]   [Persona: Demo] │
│                                                                                        │
│   ┌──────────────────────────────────────────────────────────────────────────────┐     │
│   │ SPOTLIGHT: Fullmetal Alchemist: Brotherhood (★ 9.19 | TV | Bones)            │     │
│   │ "Two brothers search for a Philosopher's Stone after a failed transmutation" │     │
│   │ [▶ View Anime Details]  [+ In Watchlist: Watching]                           │     │
│   └──────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                        │
│   Recommended For You (Rocchio Vector)    Top Rated Masterpieces (Bayesian Quality)    │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│   │ FMAB │ │Steins│ │Code G│ │Haikyu│     │CLANNAD│ │Hunter│ │Gintam│ │Cowboy│         │
│   └──────┘ └──────┘ └──────┘ └──────┘     └──────┘ └──────┘ └──────┘ └──────┘         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Deployment Status

**Deployment-ready.**

The repository includes production configuration for:
- **Render Backend**: Asynchronous FastAPI service with pre-warmed ML models and persistent disk storage for SQLite.
- **Vercel Frontend**: Optimized React 18 / Vite single-page application with SPA routing rewrites and global CDN distribution.

*A live deployment URL will be added after successful cloud deployment.* Complete step-by-step deployment instructions are provided in [`docs/deployment.md`](docs/deployment.md).

---

## Why ANIMORA?

Finding relevant anime across a catalog spanning over a century (1917–2022) is challenging for both veteran enthusiasts and newcomers:
- **Heuristic Over-Reliance**: Many platforms rely solely on raw average ratings, allowing obscure titles with 3 perfect votes (10.0) to outrank verified classics with 2,000,000 reviews.
- **Cold-Start Frustration**: New users with zero watch history are typically presented with a blank page or an unfiltered firehose of generic titles.
- **Negative Feedback Ignored**: Typical content filters only register what a user clicks on, ignoring titles the user actively dislikes.
- **Black-Box Frustration**: Users rarely understand *why* an item was recommended or have any ability to adjust recommendation criteria.

**ANIMORA** solves these challenges by combining **Rocchio user preference vectors** (incorporating both positive and negative signals), **TF-IDF content soup cosine similarity**, **Bayesian-regularized quality baselines**, **two-tier cold-start handling**, and **interactive real-time hybrid weight sliders** within a cinematic web interface.

---

## Key Features

- **Personalized Hybrid Recommendations**: Live re-ranking combining user taste vectors, item content features, and popularity signals.
- **Interactive ML Tuning Sliders**: Dynamic client-side controls for content weight ($w_{\text{content}}$), user taste weight ($w_{\text{user}}$), and popularity weight ($w_{\text{pop}}$) with immediate catalog re-ranking.
- **Two-Tier Cold-Start Strategy**: Graceful fallback for fresh accounts via genre-conditioned Bayesian rankings and catalog-wide quality diversity.
- **Fast Prefix & Fuzzy Auto-Complete Search**: Instant search across 17,495 titles with zero network lag.
- **Multi-Attribute Filtering & Catalog Discovery**: Filter by 47 distinct genres, 6 release formats (TV, Movie, OVA, Special, ONA, Music), minimum scores, and release years with paginated browsing.
- **Library & Interaction Management**: 10-star rating modals with user text reviews, multi-state watchlist tracking (`Plan to Watch`, `Watching`, `Completed`, `Dropped`), and cold-start genre preference selectors.
- **Dual Demo Personas**: Instant toggle between `Demo User (1)` (warm profile with existing ratings) and `New User (2)` (cold start) to demonstrate real-time model adaptation.
- **Responsive Cinematic Dark UI**: Built with Tailwind CSS, custom glassmorphism, Google Fonts (`Outfit` & `Inter`), accessible keyboard navigation, and route-level code splitting.

---

## Machine Learning Architecture

The recommendation engine operates across 8 modular stages:

```
                          [ Cleaned Catalog (17,495 Titles) ]
                                          │
                                          ▼
                       [ Multi-Modal Content Soup Construction ]
              (Title + Genres + Format + Studios + Source + Synopsis)
                                          │
                                          ▼
                      [ TfidfVectorizer (25,000 Unigrams/Bigrams) ]
                                          │
                                          ▼
                     [ Precomputed Sparse Matrix (tfidf_matrix.npz) ]
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
            ▼                             ▼                             ▼
   [ Content Recommender ]       [ Rocchio Taste Vector ]      [ Bayesian Quality (WR) ]
   Cosine dot product (5 ms)     α=1.0 liked, β=0.3 disliked   m=41,106 prior, C=6.51 mean
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                           [ Hybrid Linear Blending Ranker ]
              S_hybrid = (w_content * S_c) + (w_user * S_u) + (w_pop * S_p)
                                          │
                                          ▼
                           [ Ranked Top-N Recommendations ]
```

### 1. Data Preprocessing
Raw metadata from MyAnimeList is sanitized by removing malformed records, standardizing title spellings, imputing missing values (e.g. median episode counts, unknown studio tags), and extracting release years from unstructured air-date strings.

### 2. Content Representation
A rich multi-modal `content_soup` string is synthesized for every title:
```
[title] [english_title] [type] source: [source] studio: [studios] [genres] [cleaned_synopsis]
```
This ensures that studio identity, story tropes, format, and genre tags are jointly indexed alongside plot keywords.

### 3. TF-IDF Vectorization
The catalog is transformed into a 25,000-dimensional sparse feature space using `TfidfVectorizer` with:
- Sublinear term frequency scaling ($1 + \log(\text{tf})$) to dampen the impact of repeated words.
- Unigram and bigram feature extraction ($n \in \{1, 2\}$).
- Standard English stopword removal and token normalization.

### 4. Cosine Similarity
Because all TF-IDF vectors are $L_2$-normalized during vectorization, the cosine similarity between an anime query $\mathbf{v}_q$ and any candidate title $\mathbf{v}_c$ simplifies to a fast sparse dot product:
$$\text{Sim}(q, c) = \mathbf{v}_q \cdot \mathbf{v}_c$$
Executing this dot product against the sparse matrix requires only **4–8 ms** over 17,495 titles.

### 5. Popularity Baseline (Bayesian Weighted Rating)
To prevent niche anime with 3 perfect scores (10.0) from dominating quality leaderboards, ANIMORA implements the Bayesian weighted rating formulation:
$$WR = \frac{v}{v + m} R + \frac{m}{v + m} C$$
- $R$: Community mean score for the title (1.0–10.0)
- $v$: Total member votes for the title
- $m$: 80th-percentile minimum vote threshold ($m = 41,106$)
- $C$: Global mean score across rated catalog ($C = 6.51$)

A normalized log-scale popularity metric is also calculated:
$$\text{pop\_norm} = \frac{\ln(1 + v) - \min}{\max - \min}$$

### 6. Rocchio User Taste Profile
User ratings are projected directly into the continuous 25,000-dimensional TF-IDF space using Rocchio's formulation:
$$\mathbf{u} = \alpha \frac{1}{|P|} \sum_{i \in P} \mathbf{v}_i - \beta \frac{1}{|N|} \sum_{j \in N} \mathbf{v}_j$$
- Positive feedback set $P$: Titles rated $\ge 7.0$ ($\alpha = 1.0$)
- Negative feedback set $N$: Titles rated $\le 5.0$ ($\beta = 0.3$)
- Negative components are clamped to $0.0$, and the final user vector is $L_2$-normalized to $\|\mathbf{u}\|_2 = 1.0$.

### 7. Hybrid Ranking Formulation
Candidate titles are scored by a convex linear combination of content similarity, user profile affinity, and popularity:
$$S_{\text{hybrid}} = w_{\text{content}} S_{\text{content}} + w_{\text{user}} S_{\text{user}} + w_{\text{pop}} S_{\text{pop}}$$
- Constraints: $w_{\text{content}} + w_{\text{user}} + w_{\text{pop}} = 1.0$ (with $w_i \ge 0$).
- Default production weights: $w_{\text{content}} = 0.0$, $w_{\text{user}} = 0.7$, $w_{\text{pop}} = 0.3$.
- Users can adjust these weights in real time using the interactive sliders on `/recommendations`.

### 8. Two-Tier Cold-Start Strategy
- **Tier 1 (Genre-Conditioned)**: Activated when a user has no rating history but has selected preferred genres. Calculates token overlap across catalog genres and blends 60% genre affinity with 40% Bayesian quality.
- **Tier 2 (Global Diversity)**: Activated when a user has zero history and zero preferences. Returns top-tier Bayesian quality titles constrained to a maximum of 2 titles per primary genre to ensure exploration diversity.

---

## Recommendation Flow

### User-to-Item Personalized Flow
```
[User Action: Rate / Bookmark Anime]
         │
         ▼
[Fetch Active Profile (Ratings + Watchlist Exclusions + Preferences)]
         │
         ▼
[Evaluate History State]
  ├── Path A (Has Ratings):
  │     Build Rocchio vector → Dot product candidate scoring → Hybrid blend → Exclude seen titles
  │
  ├── Path B (Zero Ratings, Has Preferred Genres):
  │     Cold-Start Tier 1 → 60% Genre Overlap + 40% Bayesian WR → Exclude watchlisted titles
  │
  └── Path C (Zero Ratings, Zero Preferences):
        Cold-Start Tier 2 → Top Bayesian WR with max 2 titles per primary genre
         │
         ▼
[Return Ranked Top-N Items with Explanation Tags & Match Scores]
```

### Item-to-Item Similar Anime Flow
```
[User Views Anime Page (e.g. Death Note, mal_id: 1535)]
         │
         ▼
[Lookup Precomputed Sparse Vector for mal_id 1535 in anime_index]
         │
         ▼
[Sparse Matrix Dot Product against all 17,495 catalog vectors]
         │
         ▼
[Filter out input title itself (self-exclusion)]
         │
         ▼
[Return Top-N Nearest Titles (e.g. Death Note: Rewrite, B: The Beginning, Shinigami no Ballad)]
```

---

## Dataset

- **Primary Source**: Curated MyAnimeList anime dataset covering releases from **1917 through 2022**.
- **Raw Volume**: 24,165 uncleaned anime records.
- **Cleaned Catalog**: **17,495 production titles** after removing music duplicates, adult non-catalog entries, and records missing titles or essential metadata.
- **Key Features Available**: `mal_id`, `name`, `english_name`, `score`, `weighted_score`, `genres`, `type`, `episodes`, `members`, `release_year`, `studios`, `source`, `synopsis`, and `img_url`.
- **Deduplication**: Multi-pass deduplication based on canonical MyAnimeList ID and normalized title strings.
- **Missing Value Handling**:
  - `synopsis`: Imputed with empty string (non-blocking for TF-IDF soup).
  - `score`: Missing community ratings imputed with global catalog mean ($6.51$).
  - `episodes`: Imputed with format median (TV: 12, Movie: 1, OVA: 2).
  - `studios` / `source`: Tagged as `Unknown` if unspecified.

---

## Backend

Built as a modern asynchronous REST service using **FastAPI** and **SQLAlchemy 2.0**:
- **Application Lifespan**: The ML `RecommendationService` singleton initializes in `<150 ms` during server startup, loading precomputed sparse matrices directly into RAM.
- **Database Layer**: SQLite database (`data/animora.db`) organized in Third Normal Form (3NF) with foreign key relationships connecting anime references, user personas, ratings, watchlists, watch histories, and preference records.
- **CORS Middleware**: Configurable for development and production via `CORS_ORIGINS`.
- **Clean Architecture**: Strict separation of concerns across `routers/`, `services/`, `models/`, and `schemas/`.
- **Dependency Injection**: Reusable FastAPI dependencies for database sessions (`get_db`) and user persona resolution (`get_current_user`).

---

## Frontend

Built as a cinematic single-page application (SPA) using **React 18** and **Vite 6**:
- **Styling**: Tailwind CSS with custom dark palette (`#07090e` obsidian background, violet/amber accents, and glassmorphic panels).
- **Client Architecture**: Modular routing via React Router 6, centralized Axios client with interceptors, and React Context for active user persona and toast notifications.
- **Performance Optimization**: Route-level code splitting using `React.lazy()` and `Suspense`, reducing the initial entrypoint bundle from 325 kB to **250.75 kB** (83 kB gzipped).
- **Accessibility (a11y)**: ARIA dialog roles, accessible combobox search with keyboard arrow navigation (`ArrowUp`, `ArrowDown`, `Enter`, `Escape`), explicit form labels, and focus-visible rings.
- **Core Pages**:
  - `Home`: Spotlight hero banner, trending carousels, genre quick-filters, and personalized feed.
  - `Discover`: Catalog browsing with search auto-complete, 5 multi-attribute filter controls, and pagination.
  - `Anime Detail`: Artwork display, Bayesian scores, full synopsis, rating modal, and similar titles.
  - `Recommendations`: ML showcase with live hybrid weight sliders ($w_{\text{content}}, w_{\text{user}}, w_{\text{pop}}$) and strategy breakdown tags.
  - `Watchlist`: Status-filtered library management (`Watching`, `Plan to Watch`, `Completed`, `Dropped`).
  - `Profile`: Persona switcher, ratings history, and cold-start taste preference tuning.

---

## Project Architecture

For complete system diagrams, data flow lifecycles, and database entity relationships (ERD), see:
👉 **[`docs/architecture.md`](docs/architecture.md)**

---

## API Documentation

Interactive Swagger documentation is available at `http://localhost:8000/docs` when running the backend locally.

### Key Implemented Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check (DB connectivity & catalog records loaded) |
| `GET` | `/api/anime` | Paginated catalog with multi-attribute filtering (genre, format, score, year) |
| `GET` | `/api/anime/{id}` | Detailed anime metadata, Bayesian score, and synopsis |
| `GET` | `/api/anime/search?q={query}` | Prefix and fuzzy title auto-complete |
| `GET` | `/api/anime/{id}/similar` | Content-based recommendations using TF-IDF cosine similarity |
| `GET` | `/api/recommendations/personalized` | Hybrid Rocchio recommendations with dynamic weight parameters |
| `GET` | `/api/recommendations/popular` | Bayesian weighted score and popularity baseline recommendations |
| `POST` | `/api/ratings` | Submit user star rating (1.0–10.0) with optional review |
| `GET` | `/api/ratings` | Fetch ratings for the active user persona |
| `POST` | `/api/watchlist` | Add title to watchlist with status |
| `GET` | `/api/watchlist` | Retrieve user's watchlist |
| `DELETE` | `/api/watchlist/{id}` | Remove title from user's watchlist |
| `GET` | `/api/preferences` | Retrieve user cold-start genre/format preferences |
| `POST` | `/api/preferences` | Update user cold-start preferences |

---

## Testing & Validation

The codebase maintains a 100% automated test pass rate with zero mock data in production paths:

- **Automated Unit & Integration Tests**: **51 / 51 PASSED** (`pytest -v` in ~6.2s)
  - Content-based similarity & self-exclusion tests
  - Popularity baseline & Bayesian weighted rating tests
  - Rocchio profile vector construction & negative feedback tests
  - Hybrid linear blending & cold-start fallback tests
  - Model artifact persistence & independent reloading tests
  - Preprocessing pipeline, text normalization, and cour handling tests
  - Full FastAPI REST API endpoint contract tests
- **End-to-End API Verification**: **10 / 10 Core Contracts Verified** (`python tests/verify_integration.py`)
- **Frontend Production Build**: **0 Errors, 0 Warnings** (`npm run build` in 4.5s)

---

## Performance

All metrics reflect actual measured values from the project environment:

| Metric | Measured Value | Benchmark / Notes |
|---|---|---|
| **Catalog Scale** | **17,495 titles** | Complete cleaned MyAnimeList catalog (1917–2022) |
| **Model Size on Disk** | **9.25 MB** | Fits directly in git repository without Git LFS |
| **ML Engine Startup Time** | **<150 ms** | Instant in-memory CSR matrix load on app startup |
| **Recommendation Latency** | **4–8 ms** | Sparse vector dot product multiplication |
| **Frontend Production Bundle** | **250.75 kB JS (83.03 kB gzip)** | Code-split with `React.lazy()` & `Suspense` |
| **Frontend Production CSS** | **47.08 kB CSS (8.18 kB gzip)** | Compiled Tailwind CSS utility bundle |
| **Backend Memory Footprint** | **~280 MB RAM** | Runs comfortably within 512 MB free container limits |

---

## Local Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.11)
- Node.js 18+ & npm 9+

### 1. Clone & Set Up Backend
```bash
# Clone the repository
git clone https://github.com/your-username/Anime-Recommendation-System.git
cd Anime-Recommendation-System

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the SQLite database (takes ~3s for 17,495 records)
python -m backend.app.seed

# Start the FastAPI backend
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

### 2. Set Up Frontend
```bash
# In a new terminal window
cd frontend
npm install
npm run dev
```
*Web client available at: [http://localhost:5173](http://localhost:5173)*

### 3. Run Automated Tests
```bash
# Run all 51 backend & ML tests
pytest -v

# Run full API integration contract verification
python tests/verify_integration.py

# Verify frontend production build
cd frontend && npm run build
```

---

## Deployment

For comprehensive cloud deployment blueprints covering Vercel, Netlify, Render, Railway, Fly.io, and Docker containerization, see:
👉 **[`docs/deployment.md`](docs/deployment.md)**

---

## Repository Structure

```
Anime-Recommendation-System/
├── backend/
│   ├── README.md                    # Backend service documentation
│   └── app/
│       ├── main.py                  # FastAPI application entrypoint & lifespan
│       ├── config.py                # Pydantic Settings & environment variables
│       ├── database.py              # SQLAlchemy engine & sessionmaker
│       ├── seed.py                  # Database seeder & demo personas setup
│       ├── dependencies/            # Auth persona & database dependencies
│       ├── models/                  # AnimeReference, User, Rating, Watchlist
│       ├── schemas/                 # Pydantic request/response schemas
│       ├── services/                # RecommenderBridge, AnimeService, UserService
│       └── routers/                 # Modular API endpoints (/api/anime, /api/recommendations)
├── frontend/
│   ├── README.md                    # Frontend documentation
│   ├── src/
│   │   ├── api/                     # Centralized Axios client & endpoint wrappers
│   │   ├── context/                 # UserContext (persona toggle), ToastContext
│   │   ├── components/              # Reusable UI components (Cards, Sliders, Modals)
│   │   ├── pages/                   # Home, Discover, AnimeDetails, Recommendations, Watchlist, Profile
│   │   ├── App.jsx                  # Routing shell with React.lazy code splitting
│   │   └── index.css                # Tailwind directives, glassmorphism, scrollbars
│   ├── index.html                   # HTML entrypoint with font preconnects & SEO tags
│   ├── vercel.json                  # SPA client-side routing rewrites for Vercel
│   └── vite.config.js               # Vite configuration
├── ml/
│   ├── content_recommender.py       # TF-IDF cosine similarity model
│   ├── popularity_recommender.py    # Bayesian quality & popularity baseline
│   ├── user_profile.py              # Rocchio user taste vector builder
│   ├── cold_start.py                # Two-tier cold-start handler
│   ├── hybrid_recommender.py        # Configurable hybrid linear ranker
│   ├── recommendation_service.py    # Unified ML facade singleton
│   ├── train.py                     # Artifact training & persistence script
│   └── models/                      # Serialized model artifacts (9.25 MB total)
├── data/
│   ├── raw/                         # Raw dataset cache (.gitkeep)
│   └── processed/                   # Cleaned anime parquet (11.4 MB) & CSV datasets
├── docs/
│   ├── architecture.md              # System architecture & data flow diagrams
│   ├── deployment.md                # Cloud deployment & container guide
│   ├── DATASET.md                   # Dataset provenance & feature descriptions
│   ├── models.md                    # ML model formulation & equations
│   ├── eda_report.md                # Exploratory data analysis report
│   ├── interview.md                 # Technical interview guide & talking points
│   └── figures/                     # EDA charts & distribution figures
├── tests/                           # 51 unit & integration tests
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules for databases, node_modules, dist
├── Dockerfile                       # Production container definition
├── requirements.txt                 # Backend & ML dependencies
└── README.md                        # Master documentation
```

---

## Future Improvements

- **Two-Tower Neural Embeddings**: Train deep dual-encoder networks over user interaction sequences and item features for non-linear representation learning.
- **Offline Recommendation Benchmarking**: Implement offline evaluation harnesses comparing Hit Rate@K, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (NDCG) against historical user splits.
- **Large-Scale Vector Indexing**: Migrate in-memory dot product operations to approximate nearest neighbor (ANN) indexes (e.g., FAISS or HNSW) to scale to millions of items.
- **Direct MyAnimeList OAuth Sync**: Enable one-click import of users' personal MAL lists.

---

## License & Acknowledgments

- **License**: MIT License.
- **Dataset**: Anime data sourced from MyAnimeList via public research datasets.
- **Author**: Built as a portfolio-grade full-stack machine learning showcase.
