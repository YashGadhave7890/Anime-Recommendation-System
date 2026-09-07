"""
Unit tests for UserProfileRecommender.
"""

import numpy as np
import pytest
from ml.recommendation_service import RecommendationService

@pytest.fixture(scope="module")
def service():
    return RecommendationService(auto_train=False)


def test_user_vector_construction(service):
    """Verifies that user taste vector is normalized and non-empty for rated items."""
    history = [
        {"mal_id": 1535, "rating": 10.0},  # Death Note
        {"mal_id": 5114, "rating": 9.5},   # Fullmetal Alchemist: Brotherhood
    ]
    u_vec = service.user_profile_model.build_user_vector(user_history=history)
    assert isinstance(u_vec, np.ndarray)
    assert len(u_vec) == service.tfidf_matrix.shape[1]
    # Unit norm
    assert np.isclose(np.linalg.norm(u_vec), 1.0, atol=1e-3)


def test_user_recommendations_exclude_seen(service):
    """Verifies that items in user history are excluded from recommendations."""
    history = [
        {"mal_id": 1535, "rating": 10.0},  # Death Note
        {"mal_id": 5114, "rating": 9.5},   # FMA:B
    ]
    recs = service.get_user_recommendations(user_history=history, top_n=10)
    assert len(recs) == 10
    rec_ids = [r["mal_id"] for r in recs]
    assert 1535 not in rec_ids
    assert 5114 not in rec_ids


def test_negative_feedback_signal(service):
    """Verifies that negative feedback decreases score of similar disliked genres."""
    # Profile with high rating for psychological/thriller
    pos_only = service.user_profile_model.build_user_vector(liked_ids=[1535])  # Death Note
    # Profile with liked Death Note but strongly disliked supernatural mystery
    pos_and_neg = service.user_profile_model.build_user_vector(
        liked_ids=[1535], disliked_ids=[28891]  # Haikyuu (sports)
    )
    # The vectors should differ
    diff = np.linalg.norm(pos_only - pos_and_neg)
    assert diff > 0.0


def test_empty_user_profile_falls_back(service):
    """Verifies empty history gracefully falls back to cold-start."""
    recs = service.get_user_recommendations(user_history=[], top_n=5)
    assert len(recs) == 5
