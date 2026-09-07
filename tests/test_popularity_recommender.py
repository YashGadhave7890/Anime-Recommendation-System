"""
Unit tests for PopularityRecommender baseline.
"""

import pytest
from ml.recommendation_service import RecommendationService

@pytest.fixture(scope="module")
def service():
    return RecommendationService(auto_train=False)


def test_popularity_baseline_ranking(service):
    """Verifies baseline returns top-rated and popular anime."""
    recs = service.get_popular_recommendations(top_n=10)
    assert len(recs) == 10
    # Baseline scores should be sorted descending
    scores = [r["baseline_score"] for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_popularity_genre_filter(service):
    """Verifies genre filtering works accurately."""
    recs = service.get_popular_recommendations(genre="Action", top_n=5)
    assert len(recs) == 5
    for r in recs:
        assert "action" in r["genres"].lower()


def test_popularity_type_filter(service):
    """Verifies production format filtering (e.g. Movie, TV)."""
    recs = service.get_popular_recommendations(anime_type="Movie", top_n=5)
    assert len(recs) == 5
    for r in recs:
        assert r["type"].lower() == "movie"


def test_popularity_year_filter(service):
    """Verifies release year bounds filtering."""
    recs = service.get_popular_recommendations(min_year=2010, max_year=2020, top_n=5)
    assert len(recs) == 5
    for r in recs:
        assert 2010 <= r["release_year"] <= 2020


def test_popularity_exclude_ids(service):
    """Verifies excluded MAL IDs do not appear in recommendations."""
    top_init = service.get_popular_recommendations(top_n=3)
    exclude_id = top_init[0]["mal_id"]

    new_recs = service.get_popular_recommendations(top_n=5, exclude_ids=[exclude_id])
    assert not any(r["mal_id"] == exclude_id for r in new_recs)
