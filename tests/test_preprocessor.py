"""
Unit tests for data preprocessing and cleaning functions.
"""

import numpy as np
import pandas as pd
import pytest

from ml.preprocessor import (
    clean_missing_and_unknowns,
    deduplicate_records,
    filter_unusable_records,
)
from ml.utils import (
    clean_text,
    extract_release_info,
    parse_genres,
)


def test_clean_text():
    """Verifies that HTML entities, tags, and MAL rewrite notices are stripped cleanly."""
    raw_sample = "Kousei&#039;s story.<br />[Written by MAL Rewrite] (Source: Manga)   Extra   spaces."
    cleaned = clean_text(raw_sample)
    assert "Kousei's story." in cleaned
    assert "<br />" not in cleaned
    assert "MAL Rewrite" not in cleaned
    assert "(Source: Manga)" not in cleaned
    assert "   " not in cleaned


def test_clean_text_handles_none_and_nan():
    """Verifies clean_text gracefully handles null inputs."""
    assert clean_text(None) == ""
    assert clean_text(np.nan) == ""
    assert clean_text("") == ""


def test_parse_genres_list_string():
    """Verifies genre string formatted as list is parsed properly."""
    raw_genre = "['Action', 'Adventure', 'Fantasy']"
    genre_list, genre_str = parse_genres(raw_genre)
    assert genre_list == ["Action", "Adventure", "Fantasy"]
    assert genre_str == "Action, Adventure, Fantasy"


def test_parse_genres_comma_string():
    """Verifies comma-separated genres are parsed properly."""
    raw_genre = "Action, Comedy, Drama"
    genre_list, genre_str = parse_genres(raw_genre)
    assert genre_list == ["Action", "Comedy", "Drama"]
    assert genre_str == "Action, Comedy, Drama"


def test_parse_genres_filters_unknown():
    """Verifies 'Unknown' is filtered out of genres."""
    genre_list, genre_str = parse_genres("Unknown")
    assert genre_list == []
    assert genre_str == ""


def test_extract_release_info():
    """Verifies release year and season extraction from premiered and aired fields."""
    # From Premiered
    year, season = extract_release_info("Spring 2016", "Apr 3, 2016 to Jun 26, 2016")
    assert year == 2016
    assert season == "Spring"

    # From Aired fallback
    year2, season2 = extract_release_info("Unknown", "Oct 4, 2006 to Mar 28, 2007")
    assert year2 == 2006
    assert season2 == "Unknown"

    # Neither
    year3, season3 = extract_release_info("Unknown", "Unknown")
    assert year3 is None
    assert season3 == "Unknown"


def test_filter_unusable_records():
    """Verifies filtering of records missing title or genres."""
    df = pd.DataFrame({
        "Name": ["Anime A", "Anime B", None, "Anime D"],
        "Genres": ["Action", None, "Drama", "Unknown"],
    })
    filtered = filter_unusable_records(df)
    assert len(filtered) == 1
    assert filtered.iloc[0]["Name"] == "Anime A"


def test_deduplicate_records():
    """Verifies that duplicate titles are deduplicated keeping highest member count."""
    df = pd.DataFrame({
        "MAL_ID": [101, 102, 103],
        "Name": ["Naruto", "naruto ", "Bleach"],
        "Members": [5000, 10000, 8000],
    })
    deduped = deduplicate_records(df)
    assert len(deduped) == 2
    naruto_row = deduped[deduped["Name"].str.lower().str.strip() == "naruto"].iloc[0]
    assert naruto_row["MAL_ID"] == 102
    assert naruto_row["Members"] == 10000
