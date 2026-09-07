"""
Feature engineering module for ANIMORA anime recommendation system.
Creates content soup for NLP, Bayesian weighted ratings, log transformations,
and export formats (CSV + Parquet).
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from ml.config import (
    BAYESIAN_PERCENTILE,
    CORE_COLUMNS,
    FEATURE_METADATA_PATH,
    PROCESSED_CSV_PATH,
    PROCESSED_PARQUET_PATH,
)
from ml.preprocessor import clean_anime_dataset
from ml.utils import save_json, setup_logger

logger = setup_logger("FeatureEngineering")


def compute_bayesian_weighted_rating(
    df: pd.DataFrame,
    percentile: float = BAYESIAN_PERCENTILE,
) -> Tuple[pd.Series, float, float]:
    """
    Computes Bayesian weighted rating (IMDB / MAL formula):
        WR = (v / (v + m)) * R + (m / (v + m)) * C
    where:
        v = number of members / votes
        m = minimum votes required (quantile threshold)
        R = average score of the anime
        C = mean score across the whole dataset
        
    Returns:
        Tuple of (weighted_scores_series, m_threshold, global_mean_C)
    """
    logger.info("Computing Bayesian weighted ratings...")
    rated_mask = df["score"].notna() & (df["score"] > 0)
    
    # Global mean score C
    C = float(df.loc[rated_mask, "score"].mean())
    
    # Minimum members threshold m (e.g. 80th percentile of rated anime)
    m = float(df.loc[rated_mask, "members"].quantile(percentile))

    v = df["members"].astype(float)
    # If score is NaN (unrated), default R to C so WR evaluates cleanly to C
    R = df["score"].fillna(C).astype(float)

    weighted_score = (v / (v + m)) * R + (m / (v + m)) * C
    weighted_score = weighted_score.round(2)

    logger.info(f"Bayesian Rating Parameters: Global Mean C={C:.2f}, Threshold m={m:,.0f} members (p={percentile:.2f})")
    return weighted_score, m, C


def create_content_soup(row: pd.Series) -> str:
    """
    Constructs a rich content soup text string combining title, english name,
    genres, type, studios, source, and synopsis for NLP/content-based recommendations.
    """
    parts = []
    
    # Titles
    name = str(row.get("name", "")).strip()
    if name and name.lower() != "unknown":
        parts.append(name)
        
    eng_name = str(row.get("english_name", "")).strip()
    if eng_name and eng_name.lower() != "unknown" and eng_name.lower() != name.lower():
        parts.append(eng_name)

    # Type & Source
    an_type = str(row.get("type", "")).strip()
    if an_type and an_type.lower() != "unknown":
        parts.append(an_type)
        
    source = str(row.get("source", "")).strip()
    if source and source.lower() != "unknown":
        parts.append(f"source: {source}")

    # Studios
    studios = str(row.get("studios", "")).strip()
    if studios and studios.lower() != "unknown":
        parts.append(f"studio: {studios}")

    # Genres (weighted slightly by inclusion)
    genres = str(row.get("genres", "")).strip()
    if genres:
        parts.append(genres)

    # Clean synopsis
    synopsis = str(row.get("synopsis", "")).strip()
    if synopsis:
        parts.append(synopsis)

    soup = " ".join(parts).lower()
    return soup


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies all feature engineering transformations to cleaned anime dataset.
    """
    logger.info("Applying feature engineering transformations...")
    df = df.copy()

    # 1. Bayesian weighted rating
    weighted_score, m_val, c_val = compute_bayesian_weighted_rating(df)
    df["weighted_score"] = weighted_score

    # 2. Log-transformed community metrics
    df["log_members"] = np.log1p(df["members"]).round(4)
    df["log_favorites"] = np.log1p(df["favorites"]).round(4)

    # 3. Normalized Score [0, 1]
    min_s = float(df["score"].min()) if df["score"].notna().any() else 1.0
    max_s = float(df["score"].max()) if df["score"].notna().any() else 10.0
    df["score_norm"] = ((df["score"] - min_s) / (max_s - min_s)).round(4)

    # 4. Primary Genre
    df["primary_genre"] = df["genres_list"].apply(lambda g: g[0] if len(g) > 0 else "Unknown")

    # 5. Content Soup for Content-Based Filtering
    logger.info("Generating content soup for text embeddings...")
    df["content_soup"] = df.apply(create_content_soup, axis=1)

    # Select and order final columns
    available_cols = [c for c in CORE_COLUMNS if c in df.columns]
    # Add any extra columns useful for analysis
    extra_cols = ["genres_list", "score_norm"]
    for ec in extra_cols:
        if ec in df.columns and ec not in available_cols:
            available_cols.append(ec)

    final_df = df[available_cols].copy()

    # Metadata dictionary for export
    metadata = {
        "record_count": len(final_df),
        "columns": final_df.columns.tolist(),
        "bayesian_threshold_m": round(m_val, 2),
        "global_mean_score_c": round(c_val, 2),
        "score_min": min_s,
        "score_max": max_s,
        "types": final_df["type"].value_counts().to_dict(),
        "primary_genres_top10": final_df["primary_genre"].value_counts().head(10).to_dict(),
        "years_span": [
            int(final_df["release_year"].min()) if final_df["release_year"].notna().any() else None,
            int(final_df["release_year"].max()) if final_df["release_year"].notna().any() else None,
        ],
    }

    logger.info(f"Engineered {len(final_df):,} records with {len(final_df.columns)} features.")
    return final_df, metadata


def build_and_save_pipeline(
    output_csv: Path = PROCESSED_CSV_PATH,
    output_parquet: Path = PROCESSED_PARQUET_PATH,
    output_meta: Path = FEATURE_METADATA_PATH,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes full pipeline: load raw -> clean -> engineer features -> save artifacts.
    """
    df_clean = clean_anime_dataset()
    df_features, metadata = engineer_features(df_clean)

    # Save to CSV
    logger.info(f"Saving processed dataset to CSV: {output_csv}...")
    # Convert genres_list to string format for CSV serialization
    df_to_save = df_features.copy()
    if "genres_list" in df_to_save.columns:
        df_to_save["genres_list"] = df_to_save["genres_list"].apply(lambda x: str(x) if isinstance(x, list) else x)

    df_to_save.to_csv(output_csv, index=False, encoding="utf-8")
    logger.info(f"Saved CSV ({output_csv.stat().st_size:,} bytes).")

    # Save to Parquet
    logger.info(f"Saving processed dataset to Parquet: {output_parquet}...")
    # Parquet can handle lists or strings cleanly
    try:
        df_to_save.to_parquet(output_parquet, index=False, engine="pyarrow")
        logger.info(f"Saved Parquet ({output_parquet.stat().st_size:,} bytes).")
    except Exception as e:
        logger.warning(f"Could not save parquet with pyarrow ({e}), trying fastparquet or fallback.")
        try:
            df_to_save.to_parquet(output_parquet, index=False)
            logger.info(f"Saved Parquet ({output_parquet.stat().st_size:,} bytes).")
        except Exception as e2:
            logger.error(f"Failed to write Parquet: {e2}")

    # Save feature metadata
    save_json(metadata, output_meta)
    logger.info(f"Saved feature metadata to {output_meta}.")

    return df_features, metadata


if __name__ == "__main__":
    df_res, meta_res = build_and_save_pipeline()
    print("\n--- Feature Engineering Pipeline Summary ---")
    print(f"Final Records: {meta_res['record_count']:,}")
    print(f"Features: {meta_res['columns']}")
    print(f"Bayesian Threshold (m): {meta_res['bayesian_threshold_m']:,}")
    print(f"Global Mean (C): {meta_res['global_mean_score_c']}")
    print(f"Year Span: {meta_res['years_span']}")
