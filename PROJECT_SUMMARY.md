# ANIMORA — Project Summary

A concise quick-reference summary of the **ANIMORA — Personalized Anime Recommendation Engine** project for technical interviews, recruiters, and architecture reviews.

---

## At a Glance

| Attribute | Details |
|---|---|
| **Project Name** | **ANIMORA — Personalized Anime Recommendation Engine** |
| **Domain** | Entertainment Discovery / Machine Learning / Full-Stack Web Architecture |
| **Catalog Scale** | **17,495 cleaned anime titles** (MyAnimeList 1917–2022) |
| **Core ML Model** | Sparse TF-IDF (25,000 features) + Rocchio User Profiling + Bayesian Quality Baseline |
| **Ranking Formulation** | Linear Hybrid Blend: $S = w_{\text{content}} S_c + w_{\text{user}} S_u + w_{\text{pop}} S_p$ |
| **Backend Stack** | FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 ORM, Python 3.11 |
| **Database** | SQLite (persistent, 3NF schema) with seamless PostgreSQL compatibility |
| **Frontend Stack** | React 18, Vite 6, Tailwind CSS 3, React Router 6, Axios, Lucide Icons |
| **Test Coverage** | **51 / 51 Automated Tests Passed (100%)** via `pytest -v` |
| **Integration Contracts** | **10 / 10 Core API Contracts Verified** via `tests/verify_integration.py` |
| **Frontend Bundle** | **250.75 kB JS (83.03 kB gzip)**, **0 build errors, 0 warnings** |
| **Query Latency** | **4–8 ms** recommendation execution per request |
| **Model Size on Disk** | **9.25 MB total** (fits directly in git repository) |
| **Memory Footprint** | **~280 MB RAM** (runs comfortably on 512 MB free cloud tiers) |

---

## 1. Problem Statement

Recommending anime titles across a massive catalog spanning over a century presents unique challenges:
1. **Popularity & Small-Sample Bias**: Unreviewed titles with three 10/10 scores outrank established masterpieces with millions of votes if naive arithmetic mean scores are used.
2. **Cold-Start Failure**: New users without ratings are typically faced with empty screens or generic unpersonalized lists.
3. **Filter Bubbles & Over-Specialization**: Pure content matching recommends identical clones, while pure collaborative filtering breaks on sparse data.
4. **Lack of User Agency**: Users have no visibility into why items are recommended and no ability to adjust recommendation criteria.

---

## 2. The ANIMORA Solution

ANIMORA delivers a balanced, full-stack recommendation engine combining:
- **TF-IDF Content Similarity**: Multi-modal `content_soup` capturing genres, studios, source material, format, and synopses.
- **Bi-Directional Rocchio User Profiles**: Continuous taste vectors that amplify liked titles ($\alpha=1.0$) and actively suppress disliked tropes ($\beta=0.3$).
- **Bayesian Weighted Rating Baseline**: Regularizes community scores using an 80th-percentile prior ($m=41,106$) and global mean ($C=6.51$).
- **Interactive Linear Hybrid Ranker**: Allows users to dynamically balance content, taste, and popularity via live UI sliders.
- **Two-Tier Cold-Start Strategy**: Fallbacks to genre-conditioned Bayesian scoring (Tier 1) or diverse catalog quality (Tier 2).
- **Cinematic Responsive UI**: Route-level code-splitting, accessible search auto-complete, 10-star rating modals, and status-based watchlists.

---

## 3. Technology Stack & Key Choices

```
┌────────────────────────────────────────────────────────────────────────┐
│                              ANIMORA STACK                             │
├───────────────────┬────────────────────────────────────────────────────┤
│ Frontend Client   │ React 18.3, Vite 6.4, Tailwind CSS 3.4, Axios      │
├───────────────────┼────────────────────────────────────────────────────┤
│ Backend REST API  │ FastAPI 0.115, Uvicorn 0.28, Pydantic v2.6         │
├───────────────────┼────────────────────────────────────────────────────┤
│ Machine Learning  │ Scikit-Learn 1.6, SciPy 1.10 (CSR sparse), NumPy   │
├───────────────────┼────────────────────────────────────────────────────┤
│ Data Persistence  │ SQLite 3 (SQLAlchemy 2.0 ORM), Parquet (PyArrow)   │
├───────────────────┼────────────────────────────────────────────────────┤
│ Deployment        │ Docker, Vercel/Netlify SPA, Render/Fly.io ready   │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

## 4. Key Technical Achievements

1. **Microsecond Latency on CPU**: SciPy sparse CSR matrix multiplication achieves 4–8 ms query execution over 17,495 candidate titles without GPUs or external vector stores.
2. **Compact Serialized Footprint**: The entire precomputed model (`tfidf_matrix.npz`, `anime_index.parquet`, `tfidf_vectorizer.joblib`) requires only **9.25 MB**, loaded into RAM in `<150 ms`.
3. **True Negative Feedback Integration**: Disliked anime ($\le 5.0$) actively subtract weights from the user's Rocchio vector, suppressing unwanted tags and studios.
4. **Active Watchlist Exclusions**: Dynamically merges user ratings with multi-state watchlist items (`watching`, `completed`, `dropped`) to prevent recommending already-consumed titles.
5. **Route-Level Code Splitting**: Utilized `React.lazy()` and `Suspense` to split all 6 pages into modular chunks, reducing the initial JavaScript payload by 23% to 250 kB.
6. **Fully Accessible (a11y) Web Client**: Built accessible dialogs with keyboard `Escape` dismissal, combobox search with `ArrowUp`/`ArrowDown` navigation, and explicit form associations.
7. **100% Automated Verification**: 51 unit/integration tests (`pytest -v`) and 10 end-to-end API contracts (`verify_integration.py`) passing in ~6 seconds.

---

## 5. Deployment & Operation Status

- **Local Execution**: Standalone, reproducible locally in under 2 minutes (`python -m backend.app.seed` $\to$ `uvicorn` $\to$ `npm run dev`).
- **Container Ready**: Production `Dockerfile` based on `python:3.11-slim` with built-in healthchecks.
- **Hosting Ready**: Tested blueprints for Vercel/Netlify (static frontend SPA) and Render/Railway/Fly.io (backend web service with ~280 MB RAM footprint).
