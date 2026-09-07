"""
Unit tests for model persistence and artifact re-loading.
"""

from pathlib import Path
import pytest

from ml.config import (
    ANIME_INDEX_PATH,
    MODEL_METADATA_PATH,
    MODELS_DIR,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
)
from ml.recommendation_service import RecommendationService
from ml.utils import load_json


def test_persisted_artifacts_exist():
    """Verifies that all 4 model artifacts exist on disk and have non-zero size."""
    assert MODELS_DIR.exists()
    for path in [TFIDF_VECTORIZER_PATH, TFIDF_MATRIX_PATH, ANIME_INDEX_PATH, MODEL_METADATA_PATH]:
        assert path.exists(), f"Missing artifact: {path.name}"
        assert path.stat().st_size > 0, f"Empty artifact: {path.name}"


def test_model_metadata_structure():
    """Verifies model_metadata.json schema and expected keys."""
    meta = load_json(MODEL_METADATA_PATH)
    assert meta["model_version"] == "2.0.0"
    assert meta["total_records"] == 17495
    assert meta["vocab_size"] == 25000
    assert meta["matrix_shape"] == [17495, 25000]
    assert "artifact_paths" in meta


def test_independent_reloading_produces_identical_recommendations():
    """Verifies that freshly instantiating RecommendationService produces identical recommendations."""
    service1 = RecommendationService(auto_train=False)
    service2 = RecommendationService(auto_train=False)

    recs1 = service1.get_content_recommendations("Death Note", top_n=5)
    recs2 = service2.get_content_recommendations("Death Note", top_n=5)

    assert len(recs1) == len(recs2)
    for r1, r2 in zip(recs1, recs2):
        assert r1["mal_id"] == r2["mal_id"]
        assert r1["similarity_score"] == r2["similarity_score"]
