"""
Integration and API endpoint tests for ANIMORA FastAPI backend.
Uses Starlette/FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.seed import seed_database


@pytest.fixture(scope="module")
def client():
    """Shared TestClient fixture with initialized and seeded database."""
    seed_database(force=False)
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient):
    """Verifies GET /health endpoint status, database, and ML engine."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["ml_engine"] == "loaded"
    assert data["records_loaded"] >= 17000


def test_root_endpoint(client: TestClient):
    """Verifies root endpoint welcomes clients."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert "version" in data


def test_list_anime_paginated(client: TestClient):
    """Verifies GET /api/anime pagination and structure."""
    response = client.get("/api/anime?page=1&limit=15")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 15
    assert data["total"] >= 17000
    assert len(data["items"]) == 15
    assert "mal_id" in data["items"][0]
    assert "name" in data["items"][0]


def test_list_anime_filters(client: TestClient):
    """Verifies GET /api/anime with genre, type, score, and sort filtering."""
    response = client.get("/api/anime?genre=Action&type=TV&min_score=8.0&sort_by=score&order=desc&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10
    for item in data["items"]:
        assert "action" in item["genres"].lower()
        assert item["type"].lower() == "tv"
        assert item["score"] >= 8.0


def test_get_anime_detail(client: TestClient):
    """Verifies GET /api/anime/{id} returns details for existing title."""
    response = client.get("/api/anime/1535")  # Death Note
    assert response.status_code == 200
    data = response.json()
    assert data["mal_id"] == 1535
    assert "death note" in data["name"].lower()
    assert data["synopsis"] is not None


def test_get_anime_detail_not_found(client: TestClient):
    """Verifies GET /api/anime/{id} returns 404 for invalid ID."""
    response = client.get("/api/anime/99999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_search_anime(client: TestClient):
    """Verifies GET /api/anime/search finds matching titles."""
    response = client.get("/api/anime/search?q=hunter%20x%20hunter&limit=5")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("hunter" in r["name"].lower() for r in results)


def test_similar_anime(client: TestClient):
    """Verifies GET /api/anime/{id}/similar content-based recommendations."""
    response = client.get("/api/anime/1535/similar?top_n=5")
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "content_based"
    assert len(data["recommendations"]) == 5
    # Confirm Death Note is not its own recommendation
    for rec in data["recommendations"]:
        assert rec["mal_id"] != 1535


def test_popular_recommendations(client: TestClient):
    """Verifies GET /api/recommendations/popular baseline."""
    response = client.get("/api/recommendations/popular?genre=Sci-Fi&type=TV&top_n=5")
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "popular_baseline"
    assert len(data["recommendations"]) == 5
    for rec in data["recommendations"]:
        assert "sci-fi" in rec["genres"].lower()
        assert rec["type"].lower() == "tv"


def test_personalized_recommendations_with_history(client: TestClient):
    """Verifies GET /api/recommendations/personalized uses user ratings."""
    # Demo User 1 has ratings for Death Note, FMA:B, Steins;Gate
    response = client.get("/api/recommendations/personalized?top_n=5", headers={"X-User-Id": "1"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] in ["personalized", "hybrid"]
    assert len(data["recommendations"]) == 5
    # Rated anime should be excluded
    rec_ids = [r["mal_id"] for r in data["recommendations"]]
    assert 1535 not in rec_ids
    assert 5114 not in rec_ids


def test_cold_start_recommendations_new_user(client: TestClient):
    """Verifies GET /api/recommendations/personalized triggers cold start for user without history."""
    # Ensure Demo User 2 has 0 preferences for pure cold-start isolation
    client.post("/api/preferences", json={"preferred_genres": [], "preferred_types": []}, headers={"X-User-Id": "2"})
    response = client.get("/api/recommendations/personalized?top_n=5", headers={"X-User-Id": "2"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "cold_start_global_diverse"
    assert len(data["recommendations"]) == 5


def test_ratings_crud(client: TestClient):
    """Verifies POST /api/ratings and GET /api/ratings."""
    # Submit rating for Cowboy Bebop (MAL ID: 1)
    payload = {"anime_id": 1, "rating": 9.5, "review": "Timeless classic soundtrack and noir vibes."}
    post_res = client.post("/api/ratings", json=payload, headers={"X-User-Id": "1"})
    assert post_res.status_code in [200, 201]
    data = post_res.json()
    assert data["anime_id"] == 1
    assert data["rating"] == 9.5

    # Retrieve ratings
    get_res = client.get("/api/ratings", headers={"X-User-Id": "1"})
    assert get_res.status_code == 200
    ratings = get_res.json()
    assert any(r["anime_id"] == 1 for r in ratings)


def test_watchlist_crud(client: TestClient):
    """Verifies POST, GET, and DELETE /api/watchlist."""
    # Add Steins;Gate 0 (MAL ID: 30484) to watchlist
    payload = {"anime_id": 30484, "status": "plan_to_watch"}
    post_res = client.post("/api/watchlist", json=payload, headers={"X-User-Id": "1"})
    assert post_res.status_code == 201
    assert post_res.json()["anime_id"] == 30484

    # List watchlist
    get_res = client.get("/api/watchlist", headers={"X-User-Id": "1"})
    assert get_res.status_code == 200
    assert any(w["anime_id"] == 30484 for w in get_res.json())

    # Delete from watchlist
    del_res = client.delete("/api/watchlist/30484", headers={"X-User-Id": "1"})
    assert del_res.status_code == 204

    # Delete again should return 404
    del_again = client.delete("/api/watchlist/30484", headers={"X-User-Id": "1"})
    assert del_again.status_code == 404


def test_history_logging(client: TestClient):
    """Verifies POST and GET /api/history."""
    payload = {"anime_id": 1535, "progress_episodes": 3}
    post_res = client.post("/api/history", json=payload, headers={"X-User-Id": "1"})
    assert post_res.status_code == 201
    assert post_res.json()["progress_episodes"] == 3

    get_res = client.get("/api/history", headers={"X-User-Id": "1"})
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1


def test_preferences_and_cold_start_tuning(client: TestClient):
    """Verifies POST /api/preferences and cold start conditioning."""
    # Set preferences for User 2 (previously pure cold start)
    pref_payload = {
        "preferred_genres": ["Psychological", "Mystery"],
        "preferred_types": ["TV", "Movie"],
    }
    post_pref = client.post("/api/preferences", json=pref_payload, headers={"X-User-Id": "2"})
    assert post_pref.status_code == 200
    assert "Psychological" in post_pref.json()["preferred_genres"]

    # Now get personalized recommendations for User 2 -> should use genre-conditioned cold start!
    rec_res = client.get("/api/recommendations/personalized?top_n=5", headers={"X-User-Id": "2"})
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["strategy"] == "cold_start_genre_conditioned"
    assert len(rec_data["recommendations"]) == 5
    for rec in rec_data["recommendations"]:
        genres_lower = rec["genres"].lower()
        assert "psychological" in genres_lower or "mystery" in genres_lower
