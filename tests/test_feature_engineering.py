"""
Unit tests for feature engineering module.
"""

import numpy as np
import pandas as pd
import pytest

from ml.feature_engineering import (
    compute_bayesian_weighted_rating,
    create_content_soup,
    engineer_features,
)


def test_compute_bayesian_weighted_rating():
    """Verifies that Bayesian weighted rating computes correctly and pulls obscure titles toward the mean."""
    df = pd.DataFrame({
        "score": [9.0, 9.0, 6.0, 6.0, np.nan],
        "members": [100000, 10, 100000, 10, 500],
    })
    weighted, m, c = compute_bayesian_weighted_rating(df, percentile=0.50)
    
    assert len(weighted) == len(df)
    assert c > 0
    # The anime with score 9.0 and 100k members should stay near 9.0
    assert weighted.iloc[0] > 8.0
    # The anime with score 9.0 but only 10 members should be pulled strongly toward global mean C
    assert weighted.iloc[1] < weighted.iloc[0]
    # Unrated anime should evaluate to approximately C
    assert abs(weighted.iloc[4] - c) < 0.1


def test_create_content_soup():
    """Verifies content soup concatenates clean text components."""
    row = pd.Series({
        "name": "Fullmetal Alchemist: Brotherhood",
        "english_name": "Fullmetal Alchemist: Brotherhood",
        "genres": "Action, Adventure, Drama, Fantasy",
        "type": "TV",
        "studios": "Bones",
        "source": "Manga",
        "synopsis": "Two brothers search for a Philosopher's Stone.",
    })
    soup = create_content_soup(row)
    assert "fullmetal alchemist: brotherhood" in soup
    assert "action" in soup
    assert "bones" in soup
    assert "philosopher's stone" in soup


def test_engineer_features():
    """Verifies complete feature engineering pipeline on a sample dataframe."""
    df = pd.DataFrame({
        "mal_id": [1, 2],
        "name": ["Cowboy Bebop", "Trigun"],
        "english_name": ["Cowboy Bebop", "Trigun"],
        "japanese_name": ["カウボーイビバップ", "トライガン"],
        "score": [8.78, 8.24],
        "genres": ["Action, Sci-Fi", "Action, Sci-Fi, Comedy"],
        "genres_list": [["Action", "Sci-Fi"], ["Action", "Sci-Fi", "Comedy"]],
        "type": ["TV", "TV"],
        "episodes": [26, 26],
        "aired": ["Apr 3, 1998 to Apr 24, 1999", "Apr 1, 1998 to Sep 30, 1998"],
        "premiered": ["Spring 1998", "Spring 1998"],
        "release_year": [1998, 1998],
        "release_season": ["Spring", "Spring"],
        "producers": ["Bandai Visual", "Victor Entertainment"],
        "studios": ["Sunrise", "Madhouse"],
        "source": ["Original", "Manga"],
        "duration": ["24 min per ep", "24 min per ep"],
        "rating": ["R - 17+", "PG-13"],
        "ranked": [28.0, 250.0],
        "popularity": [39, 201],
        "members": [1251960, 558913],
        "favorites": [61971, 12944],
        "synopsis": ["Space bounty hunters.", "Vash the Stampede."],
        "img_url": ["http://img1.jpg", "http://img2.jpg"],
    })

    df_out, meta = engineer_features(df)
    assert "weighted_score" in df_out.columns
    assert "log_members" in df_out.columns
    assert "log_favorites" in df_out.columns
    assert "primary_genre" in df_out.columns
    assert "content_soup" in df_out.columns
    assert df_out["primary_genre"].iloc[0] == "Action"
    assert meta["record_count"] == 2
