"""
Automated dataset acquisition and raw data loading module.
Ensures reproducible data fetching with caching, integrity checks, and error handling.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import urllib.request
import pandas as pd

from ml.config import (
    DATASET_URLS,
    RAW_METADATA_PATH,
    RAW_SYNOPSIS_PATH,
    RAW_EXTRA_MAL_PATH,
)
from ml.utils import setup_logger

logger = setup_logger("DataLoader")


def download_file(url: str, dest_path: Path, force: bool = False, max_retries: int = 3, timeout: int = 120) -> Path:
    """
    Downloads a remote file with streaming, retries, and caching.
    
    Args:
        url: URL of the remote dataset.
        dest_path: Local destination file path.
        force: If True, re-download even if the file exists.
        max_retries: Number of retry attempts.
        timeout: Socket timeout in seconds.
        
    Returns:
        Path to the downloaded file.
    """
    if dest_path.exists() and dest_path.stat().st_size > 0 and not force:
        logger.info(f"Using cached raw file: {dest_path} ({dest_path.stat().st_size:,} bytes)")
        return dest_path

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ANIMORA-DatasetFetcher/1.0"}

    for attempt in range(1, max_retries + 1):
        logger.info(f"Downloading from {url} -> {dest_path.name} (Attempt {attempt}/{max_retries})...")
        temp_path = dest_path.with_suffix(".tmp")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response, open(temp_path, "wb") as out_file:
                block_size = 256 * 1024  # 256 KB chunks
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    out_file.write(chunk)

            # Atomic replace
            if temp_path.exists():
                temp_path.replace(dest_path)

            logger.info(f"Successfully downloaded {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
            return dest_path
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.warning(f"Attempt {attempt} failed for {url}: {e}")
            if attempt == max_retries:
                raise


def fetch_all_raw_datasets(force: bool = False) -> Dict[str, Path]:
    """Downloads all required raw anime datasets with fallback resilience."""
    logger.info("Initializing dataset acquisition for ANIMORA...")
    paths = {}
    
    # Critical datasets
    paths["metadata"] = download_file(DATASET_URLS["anime_metadata"], RAW_METADATA_PATH, force=force)
    paths["synopsis"] = download_file(DATASET_URLS["anime_synopsis"], RAW_SYNOPSIS_PATH, force=force)
    
    # Enrichment dataset (image links & additional MAL details)
    try:
        paths["extra_mal"] = download_file(DATASET_URLS["anime_extra_mal"], RAW_EXTRA_MAL_PATH, force=force)
    except Exception as e:
        logger.warning(f"Optional enrichment dataset could not be downloaded ({e}). Continuing with core datasets.")
        paths["extra_mal"] = None

    return paths


def load_raw_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Ensures raw datasets exist and loads them into pandas DataFrames.
    
    Returns:
        Tuple of (df_metadata, df_synopsis, df_extra_mal or None)
    """
    fetch_all_raw_datasets(force=False)

    logger.info("Loading raw CSV files into memory...")
    df_metadata = pd.read_csv(RAW_METADATA_PATH, low_memory=False)
    df_synopsis = pd.read_csv(RAW_SYNOPSIS_PATH, low_memory=False)
    
    df_extra_mal = None
    if RAW_EXTRA_MAL_PATH.exists() and RAW_EXTRA_MAL_PATH.stat().st_size > 0:
        try:
            df_extra_mal = pd.read_csv(RAW_EXTRA_MAL_PATH, low_memory=False)
            logger.info(f"Loaded Raw Extra MAL: {df_extra_mal.shape[0]:,} rows, {df_extra_mal.shape[1]} cols")
        except Exception as e:
            logger.warning(f"Could not parse raw extra MAL data: {e}")

    logger.info(f"Loaded Raw Metadata: {df_metadata.shape[0]:,} rows, {df_metadata.shape[1]} cols")
    logger.info(f"Loaded Raw Synopsis: {df_synopsis.shape[0]:,} rows, {df_synopsis.shape[1]} cols")

    return df_metadata, df_synopsis, df_extra_mal


if __name__ == "__main__":
    fetch_all_raw_datasets()
    df_meta, df_syn, df_mal = load_raw_datasets()
    print("\n--- Raw Data Loading Summary ---")
    print(f"Metadata Shape: {df_meta.shape}")
    print(f"Synopsis Shape: {df_syn.shape}")
    print(f"Extra MAL Shape: {df_mal.shape if df_mal is not None else 'None'}")
