"""
Unit tests for ContentRecommender.
"""

import pytest
from ml.recommendation_service import RecommendationService

@pytest.fixture(scope="module")
def service():
    """Shared RecommendationService instance."""
    return RecommendationService(auto_train=False)


def test_content_recommendations_top_n(service):
    """Verifies that requested top_n results are returned."""
    recs_5 = service.get_content_recommendations("Death Note", top_n=5)
    recs_10 = service.get_content_recommendations("Death Note", top_n=10)

    assert len(recs_5) == 5
    assert len(recs_10) == 10
    assert recs_5[0]["rank"] == 1
    assert recs_10[9]["rank"] == 10


def test_input_anime_excluded(service):
    """Verifies that the input anime is strictly not returned in recommendations."""
    query_title = "Death Note"
    recs = service.get_content_recommendations(query_title, top_n=10)
    for r in recs:
        assert r["name"].strip().lower() != query_title.lower()
        assert r["mal_id"] != 1535  # Death Note MAL ID


def test_case_insensitive_and_fuzzy_lookup(service):
    """Verifies case-insensitive and partial/fuzzy title matching."""
    # Lowercase
    recs_lower = service.get_content_recommendations("death note", top_n=5)
    assert len(recs_lower) == 5

    # Substring / partial
    recs_partial = service.get_content_recommendations("shingeki no kyojin", top_n=5)
    assert len(recs_partial) == 5

    # By MAL ID
    recs_id = service.get_content_recommendations(1535, top_n=5)
    assert len(recs_id) == 5


def test_unknown_title_handling(service):
    """Verifies that non-existent anime title raises informative ValueError."""
    with pytest.raises(ValueError) as exc_info:
        service.get_content_recommendations("CompletelyFakeAnime12345XYZ", top_n=5)
    assert "not found" in str(exc_info.value).lower()


def test_recommendation_structure(service):
    """Verifies all required metadata fields exist in recommendation outputs."""
    recs = service.get_content_recommendations("Fullmetal Alchemist: Brotherhood", top_n=3)
    required_keys = [
        "rank", "mal_id", "name", "english_name", "genres",
        "type", "score", "weighted_score", "members", "similarity_score", "img_url"
    ]
    for r in recs:
        for k in required_keys:
            assert k in r
        assert 0.0 <= r["similarity_score"] <= 1.0
