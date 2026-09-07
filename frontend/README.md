# ANIMORA — React Frontend

The modern, portfolio-grade web client for **ANIMORA — Personalized Anime Recommendation Engine**, built with **React, Vite, Tailwind CSS, React Router, and Lucide Icons**, connected to the FastAPI backend and SQLite database.

---

## 1. Features & Design Identity

- **Design Aesthetic**: Cinematic dark theme with obsidian background (`#07090e`), glassmorphic panels, gradient badges, smooth card hover transitions, and Google Fonts (`Outfit` & `Inter`).
- **Responsive Layout**: Designed for mobile, tablet, laptop, and widescreen desktop.
- **Centralized API Layer**: Centralized Axios client (`src/api/`) with automatic `X-User-Id` header routing.
- **Demo User Switcher**: Seamlessly toggle between:
  - **Demo User (ID 1)**: Trained persona with ratings, watchlist, and personalized hybrid recommendations.
  - **New User (ID 2)**: Fresh explorer persona demonstrating Two-Tier Cold-Start fallback (genre-conditioned Bayesian ranking).
- **Interactive ML Tuning**: Live sliders for $w_{\text{content}}$, $w_{\text{user}}$, and $w_{\text{pop}}$ on `/recommendations` that re-rank catalog titles in real time.
- **Interactive Interactions**: Star ratings (1–10) with text reviews, status-based bookmarking (Plan to Watch, Watching, Completed, Dropped), and genre preferences editor.

---

## 2. Available Routes

| Route | Page | Description |
|---|---|---|
| `/` | **Home** | Spotlight hero banner, trending carousels, personalized feed, popular picks, genre explorer, and "Because you liked Death Note" section. |
| `/discover` | **Discover & Search** | Prefix & fuzzy title search with live auto-complete, multi-attribute filter drawer (genres, formats, scores, sorting), and pagination. |
| `/anime/:id` | **Anime Details** | Large artwork, Bayesian scores, full plot synopsis, interactive 10-star rating modal, watchlist toggle, "Why ANIMORA Recommends This" AI breakdown, and content-based similar titles. |
| `/recommendations` | **ML Showcase** | Flagship recommendation page with interactive hybrid tuning sliders ($w_{\text{content}}, w_{\text{user}}, w_{\text{pop}}$), strategy tags, and cold-start onboarding. |
| `/watchlist` | **Watchlist** | User library with status filters (All, Watching, Plan to Watch, Completed, Dropped) and one-click removal. |
| `/profile` | **Profile & Preferences** | Persona switcher, ratings statistics, interactive genre & format preferences editor, and ratings history logs. |

---

## 3. Environment Variables

Create a `.env` file in the `frontend/` directory (or copy from `.env.example`):

```env
# Backend API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

---

## 4. Setup & Development Commands

### Prerequisites
- Node.js >= 18.0.0
- Running FastAPI backend on `http://localhost:8000`

### Installation
```bash
cd frontend
npm install
```

### Start Development Server
```bash
npm run dev
```
The application will launch on [http://localhost:5173](http://localhost:5173).

### Production Build
```bash
npm run build
```
Generates an optimized static bundle in `frontend/dist/`.

### Preview Production Build
```bash
npm run preview
```

---

## 5. API Connection Architecture

All backend communication flows through `src/api/client.js`:
- Base URL: `import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'`
- Requests automatically inject `X-User-Id` from active user context (`localStorage.getItem('animora_user_id')`).
- Handled endpoints:
  - `GET /api/anime`: Paginated catalog with multi-filters
  - `GET /api/anime/{id}`: Detailed metadata & synopsis
  - `GET /api/anime/search`: Prefix & fuzzy title auto-complete
  - `GET /api/anime/{id}/similar`: TF-IDF cosine similarity recommendations
  - `GET /api/recommendations/popular`: Bayesian quality & popularity baseline
  - `GET /api/recommendations/personalized`: Hybrid Rocchio + Content + Popularity rankings
  - `POST /api/ratings` & `GET /api/ratings`: User score submissions and review logs
  - `POST /api/watchlist`, `GET /api/watchlist`, `DELETE /api/watchlist/{id}`: Library management
  - `POST /api/preferences` & `GET /api/preferences`: Genre & format preference tuning
  - `GET /health`: Backend and ML engine health check
