"""
Unit tests for data_loader module.
"""

from pathlib import Path
import pytest

from ml.config import (
    DATASET_URLS,
    RAW_DATA_DIR,
    RAW_METADATA_PATH,
    RAW_SYNOPSIS_PATH,
)
from ml.data_loader import download_file


def test_dataset_urls_configured():
    """Verifies that all dataset URLs are defined and non-empty."""
    assert "anime_metadata" in DATASET_URLS
    assert "anime_synopsis" in DATASET_URLS
    assert DATASET_URLS["anime_metadata"].startswith("https://")
    assert DATASET_URLS["anime_synopsis"].startswith("https://")


def test_raw_files_exist_after_load():
    """Verifies that cached raw datasets exist and are non-empty."""
    assert RAW_DATA_DIR.exists()
    assert RAW_METADATA_PATH.exists()
    assert RAW_METADATA_PATH.stat().st_size > 1_000_000
    assert RAW_SYNOPSIS_PATH.exists()
    assert RAW_SYNOPSIS_PATH.stat().st_size > 1_000_000


def test_download_file_uses_cache(tmp_path: Path):
    """Verifies that download_file does not re-download if file exists and force=False."""
    dummy_file = tmp_path / "test.csv"
    dummy_file.write_text("col1,col2\nval1,val2\n", encoding="utf-8")
    initial_mtime = dummy_file.stat().st_mtime

    result_path = download_file("https://example.com/fake.csv", dummy_file, force=False)
    assert result_path == dummy_file
    assert result_path.stat().st_mtime == initial_mtime
