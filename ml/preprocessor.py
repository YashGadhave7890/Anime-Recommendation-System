"""
Data preprocessing and cleaning pipeline for ANIMORA.
Transforms raw anime datasets into a clean, validated, and standardized dataset.
"""

from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from ml.config import (
    CORE_COLUMNS,
    PROCESSED_CSV_PATH,
    PROCESSED_PARQUET_PATH,
    UNKNOWN_REPLACEMENTS,
    MIN_SCORE,
    MAX_SCORE,
)
from ml.data_loader import load_raw_datasets
from ml.utils import (
    clean_text,
    extract_release_info,
    parse_genres,
    setup_logger,
)

logger = setup_logger("Preprocessor")


def merge_raw_datasets(
    df_meta: pd.DataFrame,
    df_syn: pd.DataFrame,
    df_mal: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Merges metadata, synopsis, and extra MAL datasets using MAL_ID.
    Prioritizes complete metadata, falls back to alternative synopsis sources,
    and enriches with poster image URLs.
    """
    logger.info("Merging raw datasets...")
    df = df_meta.copy()

    # Merge synopsis from anime_with_synopsis.csv
    if "sypnopsis" in df_syn.columns:
        df_syn_subset = df_syn[["MAL_ID", "sypnopsis"]].drop_duplicates(subset=["MAL_ID"])
        df = pd.merge(df, df_syn_subset, on="MAL_ID", how="left")
    else:
        df["sypnopsis"] = np.nan

    # Merge extra MAL dataset (img_url, additional synopsis) if available
    if df_mal is not None and "uid" in df_mal.columns:
        extra_cols = ["uid"]
        if "img_url" in df_mal.columns:
            extra_cols.append("img_url")
        if "synopsis" in df_mal.columns:
            extra_cols.append("synopsis")

        df_mal_subset = df_mal[extra_cols].drop_duplicates(subset=["uid"])
        df_mal_subset = df_mal_subset.rename(columns={"uid": "MAL_ID", "synopsis": "extra_synopsis"})
        df = pd.merge(df, df_mal_subset, on="MAL_ID", how="left")
    else:
        df["img_url"] = np.nan
        df["extra_synopsis"] = np.nan

    logger.info(f"Merged raw records: {len(df):,}")
    return df


def clean_missing_and_unknowns(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces string sentinel values ('Unknown', '?', etc.) with np.nan."""
    logger.info("Normalizing sentinel unknown values...")
    cols_to_check = [
        "Score", "Episodes", "Type", "Aired", "Premiered", "Producers",
        "Licensors", "Studios", "Source", "Duration", "Rating", "Ranked",
        "Popularity", "English name", "Japanese name", "Genres", "sypnopsis", "extra_synopsis"
    ]
    for col in cols_to_check:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(UNKNOWN_REPLACEMENTS, np.nan)

    return df


def filter_unusable_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes records that cannot be used in recommendations:
    - Missing Name
    - Missing or unusable Genres
    """
    initial_count = len(df)

    # Must have a valid name
    valid_name = df["Name"].notna() & (df["Name"].astype(str).str.strip() != "")
    
    # Must have at least some genre information
    valid_genre = (
        df["Genres"].notna()
        & (~df["Genres"].astype(str).str.strip().str.lower().isin(["", "unknown", "none", "nan", "?"]))
    )

    filtered_df = df[valid_name & valid_genre].copy()
    dropped = initial_count - len(filtered_df)
    logger.info(f"Filtered out {dropped:,} unusable records (missing name or genres). Remaining: {len(filtered_df):,}")
    return filtered_df


def deduplicate_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicates records:
    1. Primary dedup by unique MAL_ID
    2. Secondary dedup by normalized lowercase name (keeping entry with highest member count)
    """
    initial_count = len(df)

    # 1. Dedup on MAL_ID
    df = df.drop_duplicates(subset=["MAL_ID"]).copy()

    # 2. Dedup on lowercase name, preserving the most popular / complete record
    df["_temp_members"] = pd.to_numeric(df["Members"], errors="coerce").fillna(0)
    df = df.sort_values(by="_temp_members", ascending=False)
    
    df["_temp_clean_title"] = df["Name"].str.lower().str.strip()
    df = df.drop_duplicates(subset=["_temp_clean_title"], keep="first")
    
    df = df.drop(columns=["_temp_members", "_temp_clean_title"])
    dropped = initial_count - len(df)
    logger.info(f"Deduplication removed {dropped:,} records. Remaining: {len(df):,}")
    return df


def parse_and_convert_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts and standardizes data types:
    - Numeric conversions (Score, Episodes, Members, Favorites, Popularity, Ranked)
    - Date and season extraction
    - Genre parsing into list and formatted string
    - Text cleaning on synopsis
    """
    logger.info("Converting numeric fields and standardizing schemas...")

    # Standardize column names to lower_snake_case
    rename_dict = {
        "MAL_ID": "mal_id",
        "Name": "name",
        "English name": "english_name",
        "Japanese name": "japanese_name",
        "Score": "score",
        "Genres": "genres_raw",
        "Type": "type",
        "Episodes": "episodes",
        "Aired": "aired",
        "Premiered": "premiered",
        "Producers": "producers",
        "Licensors": "licensors",
        "Studios": "studios",
        "Source": "source",
        "Duration": "duration",
        "Rating": "rating",
        "Ranked": "ranked",
        "Popularity": "popularity",
        "Members": "members",
        "Favorites": "favorites",
    }
    df = df.rename(columns=rename_dict)

    # Numeric fields
    df["mal_id"] = pd.to_numeric(df["mal_id"], errors="raise").astype(int)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    # Clamp valid score range [MIN_SCORE, MAX_SCORE]
    df.loc[(df["score"] < MIN_SCORE) | (df["score"] > MAX_SCORE), "score"] = np.nan

    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce")
    # If Type is Movie and episodes is NaN, impute 1
    df.loc[(df["type"].str.lower() == "movie") & (df["episodes"].isna()), "episodes"] = 1.0

    df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0).astype(int)
    df["favorites"] = pd.to_numeric(df["favorites"], errors="coerce").fillna(0).astype(int)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")
    df["ranked"] = pd.to_numeric(df["ranked"], errors="coerce")

    # Extract Release Year and Season
    years = []
    seasons = []
    for prem, air in zip(df["premiered"], df["aired"]):
        y, s = extract_release_info(prem, air)
        years.append(y)
        seasons.append(s)

    df["release_year"] = pd.Series(years, index=df.index, dtype="Int64")
    df["release_season"] = pd.Series(seasons, index=df.index, dtype="string")

    # Parse and clean genres
    genres_parsed = [parse_genres(g) for g in df["genres_raw"]]
    df["genres_list"] = [g[0] for g in genres_parsed]
    df["genres"] = [g[1] for g in genres_parsed]

    # Resolve and clean synopsis
    resolved_synopsis = df["sypnopsis"].fillna(df["extra_synopsis"])
    cleaned_synopsis = []
    for syn, name, an_type, gen in zip(resolved_synopsis, df["name"], df["type"], df["genres"]):
        clean_s = clean_text(syn)
        if not clean_s or clean_s.lower().startswith("no synopsis information"):
            # Context-aware fallback synopsis
            type_str = an_type if pd.notna(an_type) else "anime"
            gen_str = gen if gen else "various genres"
            clean_s = f"{name} is an {type_str} production exploring {gen_str}."
        cleaned_synopsis.append(clean_s)

    df["synopsis"] = cleaned_synopsis

    # Type normalization
    df["type"] = df["type"].fillna("Unknown").str.strip()

    # Clean textual metadata strings
    for str_col in ["english_name", "japanese_name", "producers", "licensors", "studios", "source", "rating"]:
        if str_col in df.columns:
            df[str_col] = df[str_col].fillna("Unknown").astype(str).str.strip()

    # Clean image URLs
    df["img_url"] = df["img_url"].fillna("")

    return df


def clean_anime_dataset() -> pd.DataFrame:
    """
    Executes the complete end-to-end data cleaning pipeline.
    
    Returns:
        Cleaned and validated pandas DataFrame.
    """
    logger.info("Starting ANIMORA data preprocessing pipeline...")
    df_meta, df_syn, df_mal = load_raw_datasets()

    df = merge_raw_datasets(df_meta, df_syn, df_mal)
    df = clean_missing_and_unknowns(df)
    df = filter_unusable_records(df)
    df = deduplicate_records(df)
    df = parse_and_convert_fields(df)

    logger.info(f"Preprocessing complete. Clean records: {len(df):,}")
    return df


if __name__ == "__main__":
    df_clean = clean_anime_dataset()
    print("\n--- Cleaned Anime Dataset Preview ---")
    print(f"Shape: {df_clean.shape}")
    print(df_clean[["mal_id", "name", "type", "score", "episodes", "members", "release_year", "genres"]].head())
