# ANIMORA Dataset Documentation

## 1. Overview & Provenance

**ANIMORA** uses real-world MyAnimeList (MAL) anime data comprising **17,562 raw entries** and **17,495 clean, validated anime titles** spanning over a century of animation history (1917 to 2022).

The data is assembled from three authoritative, publicly maintained anime repositories on GitHub:

1. **Core Metadata (`anime.csv`)**:
   - Source: [Hernan4444/MyAnimeList-Database](https://github.com/Hernan4444/MyAnimeList-Database)
   - Size: 5.66 MB (17,562 rows, 35 columns)
   - Contains: MAL ID, official title, English/Japanese titles, scores, format type, episodes, air dates, premiere season, studios, producers, source material, duration, age rating, popularity rank, member counts, favorite counts, and individual rating distributions (Score-10 through Score-1).

2. **Text Summaries (`anime_with_synopsis.csv`)**:
   - Source: [Hernan4444/MyAnimeList-Database](https://github.com/Hernan4444/MyAnimeList-Database)
   - Size: 7.22 MB (16,214 rows, 5 columns)
   - Contains: Detailed plot synopses essential for natural language processing and content-based recommendation.

3. **Community Enrichment & Visuals (`myanimelist.csv`)**:
   - Source: [cckuqui/anime-db](https://github.com/cckuqui/anime-db)
   - Size: 12.04 MB (19,311 rows, 12 columns)
   - Contains: CDN poster image URLs (`img_url`) for high-fidelity frontend presentation, MAL web links, and supplementary synopses.

---

## 2. Why This Dataset Was Selected

1. **Authenticity**: 100% genuine community data from MyAnimeList with authentic user scores, community member counts, and verified production credits.
2. **Feature Breadth**: Includes both structured categorical attributes (genres, studios, formats, source) and unstructured text (synopses), making it ideal for multi-modal recommendation algorithms.
3. **Visual Media Support**: The inclusion of authentic poster URLs (`img_url`) provides the visual assets necessary for the planned full-stack client interface in later phases.
4. **Historical Depth**: Spans anime from 1917 classics to modern broadcast releases, ensuring robust coverage of both mainstream and niche titles.

---

## 3. Manual Download Instructions (Fallback)

If automated network downloading (`python -m ml.data_loader`) is restricted by firewalls or offline environments, manually download the following files and place them into `data/raw/`:

1. **`data/raw/anime.csv`**:
   `https://raw.githubusercontent.com/Hernan4444/MyAnimeList-Database/master/data/anime.csv`
2. **`data/raw/anime_with_synopsis.csv`**:
   `https://raw.githubusercontent.com/Hernan4444/MyAnimeList-Database/master/data/anime_with_synopsis.csv`
3. **`data/raw/myanimelist.csv`** (Optional enrichment for images):
   `https://raw.githubusercontent.com/cckuqui/anime-db/master/datasets/myanimelist.csv`

---

## 4. Feature Schema (Processed Dataset)

Output location: `data/processed/cleaned_anime.csv` and `data/processed/cleaned_anime.parquet`

| Column | Type | Description |
|---|---|---|
| `mal_id` | `int64` | Unique MyAnimeList identifier |
| `name` | `string` | Primary romaji / international title |
| `english_name` | `string` | Official English title (or 'Unknown') |
| `japanese_name` | `string` | Native Japanese script title (or 'Unknown') |
| `score` | `float64` | Community score (1.0 to 10.0 scale, NaN if unrated) |
| `weighted_score` | `float64` | Bayesian weighted rating regularized against vote volume |
| `score_norm` | `float64` | Min-Max normalized score on [0, 1] scale |
| `genres` | `string` | Cleaned comma-separated genre tokens |
| `primary_genre` | `string` | First/primary categorized genre |
| `type` | `string` | Production format (`TV`, `Movie`, `OVA`, `Special`, `ONA`, `Music`) |
| `episodes` | `float64` | Number of broadcast episodes (1 for standard movies) |
| `aired` | `string` | Broadcast date range |
| `premiered` | `string` | Premier season and year (e.g. "Spring 2016") |
| `release_year` | `Int64` | Extracted integer release year |
| `release_season` | `string` | Extracted season (`Spring`, `Summer`, `Fall`, `Winter`, or `Unknown`) |
| `producers` | `string` | Production committee companies |
| `studios` | `string` | Animation studio (e.g. Bones, Madhouse, ufotable) |
| `source` | `string` | Original medium (Manga, Light novel, Original, Game, etc.) |
| `duration` | `string` | Runtime per episode/film |
| `rating` | `string` | Age rating (PG-13, R-17+, G, etc.) |
| `ranked` | `float64` | Aggregate MAL rank |
| `popularity` | `float64` | Popularity rank based on total users |
| `members` | `int64` | Number of users who added title to their list |
| `log_members` | `float64` | $\log(1 + \text{members})$ transformation |
| `favorites` | `int64` | Number of users who favorited the anime |
| `log_favorites` | `float64` | $\log(1 + \text{favorites})$ transformation |
| `synopsis` | `string` | Sanitized narrative description |
| `img_url` | `string` | Direct link to poster artwork on CDN |
| `content_soup` | `string` | Unified textual token string for NLP/content-based recommendation |
| `genres_list` | `list` / `string` | Python list representation of genres |
