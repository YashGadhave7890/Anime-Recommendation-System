"""
Configuration settings for ANIMORA ML pipeline.
Uses pathlib for platform-independent path resolution.
"""

from pathlib import Path

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Documentation & Figures Directories
DOCS_DIR = BASE_DIR / "docs"
FIGURES_DIR = DOCS_DIR / "figures"
REPORTS_DIR = DOCS_DIR / "reports"

# Model & Artifact Directories
MODELS_DIR = BASE_DIR / "ml" / "models"

# Ensure runtime directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Remote Dataset URLs (Verified authentic MyAnimeList repositories)
DATASET_URLS = {
    "anime_metadata": "https://raw.githubusercontent.com/Hernan4444/MyAnimeList-Database/master/data/anime.csv",
    "anime_synopsis": "https://raw.githubusercontent.com/Hernan4444/MyAnimeList-Database/master/data/anime_with_synopsis.csv",
    "anime_extra_mal": "https://raw.githubusercontent.com/cckuqui/anime-db/master/datasets/myanimelist.csv",
}

# Raw File Paths
RAW_METADATA_PATH = RAW_DATA_DIR / "anime.csv"
RAW_SYNOPSIS_PATH = RAW_DATA_DIR / "anime_with_synopsis.csv"
RAW_EXTRA_MAL_PATH = RAW_DATA_DIR / "myanimelist.csv"

# Processed File Paths
PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "cleaned_anime.csv"
PROCESSED_PARQUET_PATH = PROCESSED_DATA_DIR / "cleaned_anime.parquet"
FEATURE_METADATA_PATH = PROCESSED_DATA_DIR / "feature_metadata.json"
EDA_METRICS_PATH = PROCESSED_DATA_DIR / "eda_metrics.json"

# Saved Model Artifact Paths
TFIDF_VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
TFIDF_MATRIX_PATH = MODELS_DIR / "tfidf_matrix.npz"
ANIME_INDEX_PATH = MODELS_DIR / "anime_index.parquet"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Preprocessing & Cleaning Parameters
UNKNOWN_REPLACEMENTS = ["Unknown", "unknown", "UNKNOWN", "?", "-", "N/A", "nan", "None", ""]
MIN_SCORE = 1.0
MAX_SCORE = 10.0

# Bayesian Weighted Rating Parameters
# Percentile cutoff for minimum members/votes required to be considered in top rankings
BAYESIAN_PERCENTILE = 0.80

# Recommendation & NLP Modeling Hyperparameters
RANDOM_SEED = 42
TFIDF_MAX_FEATURES = 25000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_SUBLINEAR_TF = True

# User Profile / Rocchio Parameters
POSITIVE_RATING_THRESHOLD = 7.0
NEGATIVE_RATING_THRESHOLD = 5.0
ROCCHIO_ALPHA = 1.0   # Weight for positive preference signals
ROCCHIO_BETA = 0.3    # Penalty weight for negative preference signals

# Default Hybrid Weights (Item query + User profile + Popularity)
DEFAULT_HYBRID_WEIGHTS = {
    "content": 0.50,
    "user": 0.30,
    "popularity": 0.20,
}

# Default Personalized Feed Weights (No single item query)
DEFAULT_FEED_WEIGHTS = {
    "content": 0.00,
    "user": 0.70,
    "popularity": 0.30,
}

# Column Renaming / Selection
CORE_COLUMNS = [
    "mal_id",
    "name",
    "english_name",
    "japanese_name",
    "score",
    "genres",
    "type",
    "episodes",
    "aired",
    "premiered",
    "release_year",
    "release_season",
    "producers",
    "studios",
    "source",
    "duration",
    "rating",
    "ranked",
    "popularity",
    "members",
    "favorites",
    "synopsis",
    "img_url",
    "weighted_score",
    "log_members",
    "log_favorites",
    "primary_genre",
    "content_soup",
]
