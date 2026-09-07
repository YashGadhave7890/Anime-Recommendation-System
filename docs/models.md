# ANIMORA — Machine Learning Recommendation Engine Documentation

This document explains the mathematical foundations, system architecture, scoring formulations, cold-start handling, and CLI usage of the recommendation engine built in **Phase 2**.

---

## 1. System Architecture Overview

The ANIMORA recommendation engine is modular, decoupled, and persisted for sub-150ms startup times over **17,495 anime titles**:

```
ml/
├── config.py                  # Hyperparameters, persistence paths, hybrid weight profiles
├── models/                    # Serialized model artifacts
│   ├── tfidf_vectorizer.joblib# Fitted scikit-learn TfidfVectorizer (25,000 vocab)
│   ├── tfidf_matrix.npz       # Compressed CSR sparse matrix (17,495 x 25,000)
│   ├── anime_index.parquet    # Fast columnar metadata lookup table
│   └── model_metadata.json    # Versioning, diagnostics, and timestamp
├── content_recommender.py     # Content-based TF-IDF cosine recommender
├── popularity_recommender.py  # Bayesian baseline model with multi-dimensional filtering
├── user_profile.py            # Personalized user taste profile with Rocchio feedback
├── cold_start.py              # Two-tier cold-start handler (genre-conditioned vs diverse)
├── hybrid_recommender.py      # Configurable weighted hybrid ranker
├── recommendation_service.py  # Unified production API facade
├── train.py                   # Automated training & artifact serialization pipeline
└── demo.py                    # End-to-end verification and CLI demo script
```

---

## 2. Recommendation Models & Mathematical Formulations

### A. Content-Based Recommender (`ContentRecommender`)

* **Feature Representation**: Built on the engineered `content_soup` field combining:
  `{name} {english_name} {genres} {type} {studios} {source} {synopsis}`
* **Vectorization**:
  - `TfidfVectorizer` with `max_features=25,000`
  - Bi-grams: `ngram_range=(1, 2)` (captures compound terms like "time travel", "dark fantasy", "super power")
  - Sublinear term-frequency scaling: $\text{tf} = 1 + \log(\text{tf})$
  - English stop-words suppression
* **Cosine Similarity**:
  Given query vector $\vec{q} \in \mathbb{R}^{25000}$ and catalog matrix $\mathbf{V} \in \mathbb{R}^{17495 \times 25000}$:
  $$\text{sim}(\vec{q}, \mathbf{V}) = \mathbf{V} \cdot \vec{q}^T$$
  Because $\mathbf{V}$ rows and $\vec{q}$ are $L_2$-normalized, sparse matrix-vector multiplication yields exact cosine similarity in ~5–6 ms.
* **Exclusion Guarantee**: The input anime index is strictly masked out ($\text{sim} = -1.0$) so an anime is never recommended to itself.
* **Lookup**: Supports exact name, English name, MAL ID, substring, and Levenshtein fuzzy matching fallback.

---

### B. Popularity & Quality Baseline (`PopularityRecommender`)

* **Purpose**: Robust non-personalized baseline for benchmarking, cold-start fallback, and trending feeds.
* **Formulation**:
  $$\text{Score}_{baseline} = 0.70 \cdot \text{Score}_{norm}(WR) + 0.30 \cdot \text{Pop}_{norm}(\log_{1p}(members))$$
  where $WR$ is the Bayesian weighted rating from Phase 1 ($C = 6.51, m = 41,106$).
* **Filtering Capabilities**:
  - By genre (e.g. `genre="Action"` or `genre=["Sci-Fi", "Mecha"]`)
  - By format (`anime_type="TV"`, `"Movie"`, `"OVA"`, etc.)
  - By release year range (`min_year`, `max_year`)
  - By excluded seen IDs (`exclude_ids`).

---

### C. User Preference Model (`UserProfileRecommender`)

* **Purpose**: Constructs a continuous taste vector representing a user's preferences across genres, narrative tropes, themes, and studios.
* **Rocchio Feedback Formulation**:
  Supports explicit positive signals (likes / ratings $\ge 7.0$) and negative signals (dislikes / ratings $\le 5.0$):
  $$\vec{u}_{raw} = \alpha \cdot \frac{1}{|P|} \sum_{i \in P} w_i \vec{v}_i - \beta \cdot \frac{1}{|N|} \sum_{j \in N} w_j \vec{v}_j$$
  where:
  - $P$ is the set of positive items with rating weights $w_i = \text{rating} - 6.0$
  - $N$ is the set of negative items with penalty weights $w_j = 6.0 - \text{rating}$
  - $\alpha = 1.0$ (positive pull), $\beta = 0.3$ (negative repulsion)
  - Negative values are zero-clamped: $\vec{u} = \max(\vec{u}_{raw}, 0)$
  - Normalized: $\vec{u} = \frac{\vec{u}}{\|\vec{u}\|_2}$
* **Recommendation Score**:
  $$\text{Score}_{user}(k) = \mathbf{V}_k \cdot \vec{u}^T$$
  All previously rated or liked anime are excluded from the candidate output.

---

### D. Hybrid Recommender (`HybridRecommender`)

* **Unified Linear Blending Formula**:
  $$\text{Score}_{hybrid}(k) = w_{content} \cdot S_{content}(k) + w_{user} \cdot S_{user}(k) + w_{pop} \cdot S_{pop}(k)$$
  where $\sum w_i = 1.0$.
* **Operational Modes**:
  1. **Item-Focused Hybrid** (User viewing an anime page with their profile active):
     `w_content = 0.50, w_user = 0.30, w_pop = 0.20`
  2. **Personalized Feed** (No single query anime, pure user profile):
     `w_content = 0.00, w_user = 0.70, w_pop = 0.30`
  3. **Item-Only Hybrid** (Anonymous visitor on anime page):
     `w_content = 0.75, w_user = 0.00, w_pop = 0.25`
  4. **Custom Weights**: Caller can supply runtime weights (e.g. `weights={"content": 0.8, "user": 0.1, "popularity": 0.1}`).

---

### E. Cold-Start Strategy (`ColdStartHandler`)

When user history is absent or sparse:

1. **Tier 1 (Genre-Conditioned)**:
   When user specifies preferred genres (e.g. `["Sci-Fi", "Mecha"]`):
   $$\text{Score}_{cold} = 0.60 \cdot \text{Overlap}_{norm}(\text{genres}) + 0.40 \cdot \text{Score}_{baseline}$$
   Ranks the most representative, critically acclaimed anime within those genres.
2. **Tier 2 (Global Diverse Baseline)**:
   When zero information is available:
   Pulls candidates from the top Bayesian baseline while enforcing genre diversity (capping recommendations per primary genre) to prevent single-franchise monopolization.

---

## 3. Real Example Recommendations

### Content-Based: Query `Death Note`
| Rank | Title | Format | Year | Similarity | Genres |
|---|---|---|---|---|---|
| #1 | *Death Note: Rewrite* | Special | 2007 | 0.3653 | Mystery, Police, Psychological |
| #2 | *B: The Beginning Succession* | ONA | 2021 | 0.1639 | Action, Mystery, Police, Psychological |
| #3 | *Shinigami no Ballad.* | TV | 2006 | 0.1555 | Drama, Fantasy, Psychological |
| #4 | *Yami no Matsuei* | TV | 2000 | 0.1452 | Comedy, Drama, Fantasy, Horror |
| #5 | *B: The Beginning* | ONA | 2018 | 0.1339 | Action, Mystery, Police, Psychological |

*(Notice: "Death Note" is strictly excluded; recommendations capture the psychological detective and shinigami themes).*

---

### Cold-Start Tier 1: Selected Genres `['Sci-Fi', 'Mecha']`
| Rank | Title | Format | Year | Cold Score | Genres |
|---|---|---|---|---|---|
| #1 | *Code Geass: Hangyaku no Lelouch R2* | TV | 2008 | 0.9768 | Action, Military, Sci-Fi, Super Power |
| #2 | *Code Geass: Hangyaku no Lelouch* | TV | 2006 | 0.9692 | Action, Military, Sci-Fi, Super Power |
| #3 | *Tengen Toppa Gurren Lagann* | TV | 2007 | 0.9631 | Action, Adventure, Comedy, Mecha |
| #4 | *Neon Genesis Evangelion: The End of Evangelion* | Movie | 1997 | 0.9451 | Sci-Fi, Dementia, Psychological |
| #5 | *Neon Genesis Evangelion* | TV | 1995 | 0.9445 | Action, Sci-Fi, Dementia, Psychological |

---

### Pure Cold-Start Tier 2: Diverse Global Baseline
| Rank | Title | Format | Year | Baseline Score | Primary Genre |
|---|---|---|---|---|---|
| #1 | *Fullmetal Alchemist: Brotherhood* | TV | 2009 | 0.9970 | Action |
| #2 | *Steins;Gate* | TV | 2011 | 0.9795 | Thriller |
| #3 | *Hunter x Hunter (2011)* | TV | 2011 | 0.9769 | Action |
| #4 | *Kimi no Na wa.* | Movie | 2016 | 0.9582 | Romance |
| #5 | *Koe no Katachi* | Movie | 2016 | 0.9576 | Drama |

---

## 4. Persisted Model Artifacts

Output directory: `ml/models/`

| Artifact | Size | Description |
|---|---|---|
| `tfidf_vectorizer.joblib` | 283 KB | Fitted scikit-learn `TfidfVectorizer` |
| `tfidf_matrix.npz` | 7.39 MB | Compressed CSR sparse matrix ($17,495 \times 25,000$) |
| `anime_index.parquet` | 1.58 MB | Optimized columnar lookup table |
| `model_metadata.json` | 527 bytes | Training timestamp, vocab size, hyperparameters |

Total artifact bundle is **< 10 MB**, allowing instant loading in production environments.

---

## 5. Commands to Run Phase 2

```bash
# 1. Train and serialize model artifacts to ml/models/
python -m ml.train

# 2. Run the complete interactive CLI verification demo
python -m ml.demo

# 3. Run all automated unit tests (Phase 1 + Phase 2: 36 tests)
pytest -v
```
