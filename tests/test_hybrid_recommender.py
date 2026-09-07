"""
Unit tests for HybridRecommender and ColdStartHandler.
"""

import pytest
from ml.recommendation_service import RecommendationService

@pytest.fixture(scope="module")
def service():
    return RecommendationService(auto_train=False)


def test_hybrid_with_item_and_user_history(service):
    """Verifies hybrid recommendations combine content, user history, and popularity."""
    history = [{"mal_id": 5114, "rating": 9.0}]  # FMA:B
    recs = service.get_hybrid_recommendations(
        query_anime="Death Note",
        user_history=history,
        top_n=5,
    )
    assert len(recs) == 5
    for r in recs:
        assert "hybrid_score" in r
        assert "content_score" in r
        assert "user_score" in r
        assert "popularity_score" in r
        # Query anime and history excluded
        assert r["mal_id"] != 1535
        assert r["mal_id"] != 5114


def test_hybrid_custom_weights(service):
    """Verifies custom weights are applied and recorded in results."""
    custom_w = {"content": 0.8, "user": 0.1, "popularity": 0.1}
    recs = service.get_hybrid_recommendations(
        query_anime="Death Note",
        weights=custom_w,
        top_n=3,
    )
    assert len(recs) == 3
    for r in recs:
        assert r["weights_used"]["content"] == 0.8


def test_cold_start_genre_conditioned(service):
    """Verifies cold-start recommendations with selected genres."""
    recs = service.get_cold_start_recommendations(selected_genres=["Sports"], top_n=5)
    assert len(recs) == 5
    for r in recs:
        assert "sports" in r["genres"].lower()


def test_pure_cold_start_diversity(service):
    """Verifies global cold-start provides diverse recommendations."""
    recs = service.get_cold_start_recommendations(top_n=10)
    assert len(recs) == 10
    # Diverse genres
    genres = [r["genres"] for r in recs]
    assert len(set(genres)) >= 5


def test_search_anime(service):
    """Verifies title search auto-complete function."""
    results = service.search_anime("hunter x hunter", limit=5)
    assert len(results) >= 1
    assert any("hunter" in r["name"].lower() for r in results)
