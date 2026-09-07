# ANIMORA — Portfolio & Profile Description Report

> **Project Name**: ANIMORA — Personalized Anime Recommendation Engine  
> **Repository**: [https://github.com/YashGadhave7890/Anime-Recommendation-System](https://github.com/YashGadhave7890/Anime-Recommendation-System)  
> **Author**: Yash Gadhave  
> **Status**: Production-Ready / Live Operational  

---

## Executive Summary

**ANIMORA** is a portfolio-grade, full-stack machine learning recommendation platform indexing **17,495 authentic MyAnimeList titles** (1917–2022). Rather than relying on simplistic nearest-neighbor heuristics or naive averages that suffer from popularity bias and cold-start dead ends, ANIMORA implements a **tri-hybrid recommendation engine**:
1. **Content-Based Similarity**: Multi-modal `content_soup` vectorized across 25,000 TF-IDF features with sublinear term-frequency scaling.
2. **Bi-Directional Rocchio Taste Vectors**: Projects positive user ratings ($\ge 7.0$, $\alpha=1.0$) and negative ratings ($\le 5.0$, $\beta=0.3$) into the continuous semantic space to steer recommendations toward preferred themes and away from unwanted tropes.
3. **Bayesian Weighted Rating Baseline**: Regularizes community scores against an 80th-percentile prior ($m=41,106$, $C=6.51$) to resolve small-sample bias.
4. **Two-Tier Cold-Start Engine**: Automatically routes new users through genre-conditioned Bayesian scoring (Tier 1) or catalog-wide quality diversity (Tier 2).

The backend is built with **FastAPI** and **SQLAlchemy 2.0 ORM** (3NF SQLite database), serving queries in **4–8 ms** within a **~280 MB RAM** container envelope. The frontend is a cinematic single-page application built with **React 18**, **Vite 6**, and **Tailwind CSS**, featuring live recommendation tuning sliders, accessible combobox search, and route-level lazy loading (250 kB initial bundle).

---

## 1. GitHub Profile & Repository Presentation

### Repository "About" Description (Max 350 characters)
```text
Portfolio-grade full-stack anime recommendation engine over 17,495 MAL titles. Built with TF-IDF cosine similarity, Rocchio user preference vectors, Bayesian quality baselines, FastAPI backend, and React 18 cinematic UI with live ML tuning sliders.
```

### GitHub Repository Topics / Tags
```text
machine-learning, recommendation-system, fastapi, react, tailwindcss, vite, tfidf, rocchio-algorithm, bayesian-ranking, sqlite, sqlalchemy, python, portfolio
```

### GitHub Profile README Feature Card (Markdown)
```markdown
### 🌟 Featured Project: [ANIMORA — Personalized Anime Recommendation Engine](https://github.com/YashGadhave7890/Anime-Recommendation-System)

> **Discover what you'll love next.** Full-stack ML platform indexing 17,495 MyAnimeList titles with sub-10ms recommendation latency.

- **Machine Learning**: 25k-dimensional TF-IDF content soup + Rocchio user profile vectors (positive + negative feedback) + Bayesian-regularized quality baselines.
- **Backend**: Asynchronous FastAPI REST service with SQLAlchemy ORM, pre-warmed ML singleton, and dynamic CORS.
- **Frontend**: Cinematic React 18 + Vite + Tailwind CSS single-page app with live hybrid tuning sliders and full ARIA accessibility.
- **Testing & Performance**: 52/52 automated tests passing, 10/10 API integration contracts verified, 250 kB initial bundle.

👉 **[View Repository & Architecture Docs](https://github.com/YashGadhave7890/Anime-Recommendation-System)**
```

---

## 2. LinkedIn Profile & Featured Post

### LinkedIn "Projects" Section Entry

- **Project Name**: ANIMORA — Personalized Anime Recommendation Engine
- **Associated With**: Independent Machine Learning / Full-Stack Project
- **Project URL**: `https://github.com/YashGadhave7890/Anime-Recommendation-System`
- **Skills**: Machine Learning, Python, FastAPI, React.js, Scikit-Learn, Information Retrieval (TF-IDF & Rocchio), SQLAlchemy, Tailwind CSS, System Design, Docker

**Description**:
```text
Architected and deployed ANIMORA, an end-to-end full-stack anime recommendation engine indexing 17,495 MyAnimeList titles (1917–2022) with sub-10ms query execution.

Key Accomplishments:
• Designed a hybrid recommendation pipeline combining 25,000-feature TF-IDF content similarity, Bayesian weighted rating quality baselines (m=41,106), and bi-directional Rocchio taste vectors incorporating both positive (≥7.0) and negative (≤5.0) user signals.
• Implemented a two-tier cold-start fallback strategy (genre-conditioned Bayesian scoring and catalog diversity) to prevent empty-state dead ends for fresh accounts.
• Engineered an asynchronous FastAPI REST backend loading the precomputed 9.25 MB sparse ML model into memory in <150 ms, operating within a ~280 MB RAM container footprint.
• Built a cinematic, accessible React 18 + Vite frontend featuring live hybrid tuning sliders (wc, wu, wp), search auto-complete, and route-level code splitting (250 kB JS payload).
• Validated through 52 automated Pytest unit/integration tests and 10 end-to-end API integration contracts with 100% pass rate.
```

---

### LinkedIn Announcement / Showcase Post

```markdown
🚀 Excited to share my latest full-stack machine learning project: **ANIMORA — Personalized Anime Recommendation Engine**!

When discovering media across decades of releases, most recommendation platforms either recommend the same 5 mainstream hits (popularity bias) or show completely unrated obscure titles with three 10/10 ratings (small-sample bias). Even worse, cold-start users are left staring at empty screens.

I built **ANIMORA** from scratch to solve these exact discovery challenges across **17,495 authentic MyAnimeList titles** (1917–2022).

🧠 **How the Machine Learning Engine Works:**
1️⃣ **Multi-Modal Content Soup**: Vectorizes anime synopses, genres, studios, source material, and formats into a 25,000-dimensional sparse TF-IDF space with sublinear term-frequency scaling.
2️⃣ **Bi-Directional Rocchio User Modeling**: Projects user ratings directly into semantic space—amplifying liked themes (α=1.0) while actively subtracting disliked tropes (β=0.3) so unwanted genres are suppressed.
3️⃣ **Bayesian Weighted Quality Baseline**: Applies an 80th-percentile Bayesian prior (m=41,106) to prevent small-sample rating distortion.
4️⃣ **Linear Hybrid Blending**: Allows users to dynamically balance content similarity, personal taste, and popularity via real-time UI tuning sliders.
5️⃣ **Two-Tier Cold-Start Strategy**: Seamlessly routes new users through genre-conditioned rankings or diverse catalog quality baselines.

⚡ **Tech Stack & System Architecture:**
• **Backend**: FastAPI, SQLAlchemy 2.0 ORM, SQLite (3NF schema), Pydantic v2, Uvicorn ASGI.
• **Frontend**: React 18, Vite 6, Tailwind CSS 3, Lucide Icons.
• **Performance**: 4–8 ms recommendation execution, <150 ms startup warmup, 9.25 MB serialized model footprint, and a 250 kB code-split JavaScript bundle.
• **Reliability**: 52 automated tests passing (100%), 10 API integration contracts verified, and full Docker containerization.

💻 **Check out the source code, architecture diagrams, and mathematical formulation on GitHub:**
🔗 https://github.com/YashGadhave7890/Anime-Recommendation-System

Feedback, thoughts, and stars are always welcome! ⭐

#MachineLearning #DataScience #Python #FastAPI #React #FullStack #ArtificialIntelligence #InformationRetrieval #SoftwareEngineering #Portfolio
```

---

## 3. Resume / CV Project Bullets

### Option A: Machine Learning / AI Engineer Focus
- **ANIMORA — Personalized Anime Recommendation Engine** *(Python, FastAPI, Scikit-Learn, NumPy, SciPy)*
  - Developed a full-stack recommendation engine over 17,495 MyAnimeList titles, achieving 4–8 ms query latencies using sparse TF-IDF matrix dot products across 25,000 unigram/bigram features.
  - Implemented bi-directional Rocchio taste vectors incorporating positive ($\ge 7.0$) and negative ($\le 5.0$) rating feedback, combined with Bayesian weighted ratings ($m=41,106$) and two-tier cold-start handling.
  - Serialized precomputed sparse models into a 9.25 MB footprint, reducing backend boot warm-up to <150 ms within a ~280 MB RAM container budget; verified via 52 automated tests (100% pass rate).

### Option B: Full-Stack Software Engineer Focus
- **ANIMORA — Full-Stack Anime Discovery Platform** *(React 18, Vite, Tailwind CSS, FastAPI, SQLite)*
  - Engineered a cinematic single-page discovery application featuring instant search auto-complete, 5 multi-attribute filters, 10-star rating modals, and live recommendation weight sliders.
  - Implemented client-side performance optimizations with `React.lazy()` and `Suspense`, cutting initial bundle size by 23% to 250 kB, with full WCAG-compliant keyboard navigation (dialog, combobox).
  - Built an asynchronous FastAPI REST service with SQLAlchemy ORM, dynamic CORS, 3NF SQLite schema, and Docker containerization; verified 10 core API integration contracts.

### Option C: Backend / Systems Engineer Focus
- **ANIMORA — Asynchronous Recommendation Service** *(Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn)*
  - Designed an asynchronous REST API connecting a 17.5k-record SQLite relational database to an in-memory sparse ML recommendation singleton, serving cached and dynamic personalized queries in <10 ms.
  - Formulated dynamic CORS handling, healthcheck diagnostics, and environment-driven SQLite persistent volume resolution for Render and Docker cloud deployments.
  - Enforced strict request/response serialization with Pydantic v2 schemas; authored comprehensive automated integration suites maintaining a 100% pass rate across 52 test cases.

---

## 4. Portfolio Website Case Study & Architecture Overview

### Overview Card
- **Project**: ANIMORA
- **Category**: Machine Learning & Full-Stack Web Development
- **Role**: Sole Architect & Developer
- **Duration**: Complete 7-Phase Engineering Lifecycle
- **Status**: Live / Production-Ready
- **Stack**: Python, Scikit-Learn, FastAPI, SQLite, React 18, Vite, Tailwind CSS, Docker

### Problem Statement
Online entertainment catalogs suffer from two severe user experience failures:
1. **The Popularity Echo Chamber**: Simple average scores rank titles with 3 five-star reviews above classics with 2,000,000 reviews, while collaborative filtering fails on cold-start users.
2. **The "Black Box" Frustration**: Recommender systems offer users zero transparency into recommendation logic and zero control over ranking priorities.

### The Solution: Tri-Hybrid Linear Blending with User Agency
ANIMORA gives users full control through an interactive hybrid linear formulation:
$$S_{\text{hybrid}} = w_{\text{content}} S_{\text{content}} + w_{\text{user}} S_{\text{user}} + w_{\text{pop}} S_{\text{pop}}$$
- **Content Similarity ($S_{\text{content}}$)**: Measures semantic plot and metadata overlap against a query anime.
- **User Preference Affinity ($S_{\text{user}}$)**: Cosine similarity against a Rocchio user profile vector calculated from explicit ratings.
- **Popularity & Quality ($S_{\text{pop}}$)**: Bayesian-regularized score balancing community consensus and member reach.
- Users can dynamically manipulate $w_{\text{content}}$, $w_{\text{user}}$, and $w_{\text{pop}}$ using real-time sliders in the UI to transition from exploratory discovery to hyper-personalized feeds.

---

## 5. Key Verified Metrics

| Metric | Measured Value | Benchmark / Target | Status |
|---|---|---|---|
| **Catalog Scale** | **17,495 anime titles** | Complete cleaned MAL catalog (1917–2022) | Verified |
| **Model Size on Disk** | **9.25 MB total** | `<10 MB` (Fits directly in GitHub repository) | Verified |
| **ML Engine Startup Time** | **<150 ms** | Instant in-memory CSR matrix load | Verified |
| **Recommendation Latency** | **4–8 ms** | Sparse matrix dot product on CPU | Verified |
| **Backend Memory Footprint** | **~280 MB RAM** | Fits inside 512 MB free cloud container tiers | Verified |
| **Frontend Production Bundle** | **250.75 kB JS (83.03 kB gzip)** | 23% reduction via route code splitting | Verified |
| **Automated Test Suite** | **52 / 52 PASSED (100%)** | Full unit, ML, and API test coverage | Verified |
| **Full-Stack API Contracts** | **10 / 10 Operational** | End-to-end integration verified | Verified |
| **Production Smoke Tests** | **12 / 12 Operational** | Non-destructive safe read-only checks | Verified |

---

## 6. Live Execution & Demonstration Commands

To run ANIMORA locally or demonstrate live:

```bash
# 1. Clone repository
git clone https://github.com/YashGadhave7890/Anime-Recommendation-System.git
cd Anime-Recommendation-System

# 2. Set up backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app.seed
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Set up frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

- **Web Application**: `http://localhost:5173`
- **Interactive OpenAPI Explorer**: `http://localhost:8000/docs`
- **Health Check Endpoint**: `http://localhost:8000/health`
- **Automated Verification**: `pytest -v` and `python tests/production_smoke_test.py`
