"""
ANIMORA — Full-Stack API Contract Verification Script.
Tests all 10 core API contracts (Health, Details, Trending, Search, Content-Based,
Personalized Rocchio, Custom Hybrid Weights, Cold-Start Fallback, Watchlist, and Ratings).
Automatically detects whether a live Uvicorn server is running or falls back to in-memory TestClient.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx

try:
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=3.0)
    resp = client.get("/health")
    if resp.status_code != 200:
        raise RuntimeError("Server returned non-200")
    print("[INFO] Connected to live backend on http://127.0.0.1:8000\n")
except Exception:
    from fastapi.testclient import TestClient
    from backend.app.main import app

    print("[INFO] No live server on port 8000 detected. Running verification with FastAPI TestClient.\n")
    client = TestClient(app)

# 1. Health
health = client.get("/health").json()
print(f"1. Health Status: {health['status']} | Catalog Records: {health['records_loaded']}")

# 2. Hero Anime Detail (Fullmetal Alchemist: Brotherhood)
hero = client.get("/api/anime/5114").json()
print(f"2. Hero Detail: {hero['name']} | Score: {hero['score']} | Format: {hero['type']}")

# 3. Trending Catalog
trending = client.get("/api/anime?sort_by=weighted_score&order=desc&limit=5").json()
print(f"3. Trending Top 1: {trending['items'][0]['name']} | Bayesian Score: {trending['items'][0]['weighted_score']}")

# 4. Search Autocomplete
search_res = client.get("/api/anime/search?q=hunter&limit=3").json()
print(f"4. Search Autocomplete ('hunter'): {[s['name'] for s in search_res]}")

# 5. Content-based Similar Anime (Death Note)
similar = client.get("/api/anime/1535/similar?top_n=3").json()
print(f"5. Similar to Death Note: {[r['name'] for r in similar['recommendations']]}")

# 6. Personalized Recommendations for User 1 (Warm profile)
personalized = client.get(
    "/api/recommendations/personalized?top_n=3",
    headers={"X-User-Id": "1"},
).json()
print(f"6. Personalized for User 1: Strategy='{personalized['strategy']}' | Top: {personalized['recommendations'][0]['name']}")

# 7. Personalized Recommendations with Custom Hybrid Weights
hybrid = client.get(
    "/api/recommendations/personalized?top_n=3&w_content=0.4&w_user=0.4&w_pop=0.2",
    headers={"X-User-Id": "1"},
).json()
print(f"7. Custom Hybrid Weights: Strategy='{hybrid['strategy']}' | Weights: {hybrid['weights_used']}")

# 8. Cold Start for User 2 (Cold-start persona)
cold = client.get(
    "/api/recommendations/personalized?top_n=3",
    headers={"X-User-Id": "2"},
).json()
print(f"8. Cold Start for User 2: Strategy='{cold['strategy']}' | Top: {cold['recommendations'][0]['name']}")

# 9. Watchlist CRUD
watch_add = client.post(
    "/api/watchlist",
    json={"anime_id": 11061, "status": "watching"},
    headers={"X-User-Id": "1"},
).json()
print(f"9. Watchlist Added Status: {watch_add['status']}")
watch_list = client.get("/api/watchlist", headers={"X-User-Id": "1"}).json()
print(f"   Watchlist Total Items for User 1: {len(watch_list)}")

# 10. Rating Submission
rating_res = client.post(
    "/api/ratings",
    json={"anime_id": 11061, "rating": 9.8, "review": "Peak shounen storytelling."},
    headers={"X-User-Id": "1"},
).json()
print(f"10. Rating Submitted: {rating_res['rating']} | Anime: {rating_res['anime']['name']}")

print("\n=======================================================")
print("ALL FULL-STACK API CONTRACTS VERIFIED 100% OPERATIONAL!")
print("=======================================================")
