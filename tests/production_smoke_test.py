"""
ANIMORA — Production Pre-Flight & Post-Deployment Smoke Test Script.

This script executes safe, non-destructive read-only GET requests against a target
ANIMORA API server (locally on localhost or remotely on Render/Cloud).

Configured via environment variable:
    ANIMORA_API_URL (default: http://localhost:8000)

Usage:
    # Test local server
    python tests/production_smoke_test.py

    # Test deployed Render backend
    set ANIMORA_API_URL=https://your-service.onrender.com
    python tests/production_smoke_test.py
"""

import os
import sys
import time
from pathlib import Path

# Add project root to sys.path for in-memory fallback if needed
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx


def get_client(target_url: str):
    """Returns an HTTP client or in-process FastAPI TestClient."""
    try:
        live_client = httpx.Client(base_url=target_url, timeout=15.0)
        resp = live_client.get("/health")
        if resp.status_code == 200:
            return live_client, False
    except Exception:
        pass

    if "localhost" in target_url or "127.0.0.1" in target_url:
        from fastapi.testclient import TestClient
        from backend.app.main import app

        return TestClient(app), True

    raise RuntimeError(f"Could not connect to remote backend at {target_url}")


def run_smoke_tests(standalone: bool = True) -> int:
    """Executes all safe read-only smoke tests."""
    target_url = os.getenv("ANIMORA_API_URL", "http://localhost:8000").rstrip("/")

    if standalone:
        print(f"===========================================================")
        print(f"  ANIMORA Production Smoke Test")
        print(f"  Target URL: {target_url}")
        print(f"===========================================================\n")

    client, using_test_client = get_client(target_url)

    if standalone:
        if using_test_client:
            print(f"[NOTICE] No standalone server running at {target_url}.")
            print("[INFO] Running verification via in-memory FastAPI TestClient.\n")
        else:
            print(f"[SUCCESS] Connected to live backend at {target_url}\n")

    passed = 0
    failed = 0

    def run_check(title: str, method: str, path: str, headers: dict = None, validate_fn=None):
        nonlocal passed, failed
        t0 = time.time()
        try:
            res = client.request(method, path, headers=headers)
            elapsed_ms = (time.time() - t0) * 1000

            if res.status_code not in (200, 201):
                if standalone:
                    print(f"  [FAIL] {title} ({path}) -> HTTP {res.status_code} ({elapsed_ms:.1f}ms)")
                failed += 1
                return None

            data = res.json()
            if validate_fn:
                validation_err = validate_fn(data)
                if validation_err:
                    if standalone:
                        print(f"  [FAIL] {title} ({path}) -> Validation error: {validation_err}")
                    failed += 1
                    return None

            if standalone:
                print(f"  [PASS] {title} ({path}) -> HTTP {res.status_code} ({elapsed_ms:.1f}ms)")
            passed += 1
            return data
        except Exception as exc:
            if standalone:
                print(f"  [FAIL] {title} ({path}) -> Exception: {exc}")
            failed += 1
            return None

    # 1. Healthcheck
    run_check(
        "1. Health Check",
        "GET",
        "/health",
        validate_fn=lambda d: None if d.get("status") in ("healthy", "degraded") else f"Unexpected status: {d.get('status')}",
    )

    # 2. Root API Welcome
    run_check(
        "2. Root Endpoint",
        "GET",
        "/",
        validate_fn=lambda d: None if "docs" in d else "Missing 'docs' field in root response",
    )

    # 3. Catalog Paginated List
    run_check(
        "3. Catalog Paginated List",
        "GET",
        "/api/anime?limit=5",
        validate_fn=lambda d: None if len(d.get("items", [])) == 5 else f"Expected 5 items, got {len(d.get('items', []))}",
    )

    # 4. Catalog Multi-Attribute Filter (TV, Action, Min Score 8.0)
    run_check(
        "4. Catalog Filter (TV, Action, Score >= 8.0)",
        "GET",
        "/api/anime?type=TV&genre=Action&min_score=8.0&limit=3",
        validate_fn=lambda d: None if d.get("total", 0) > 0 else "Expected non-zero filtered results",
    )

    # 5. Anime Detail (Fullmetal Alchemist: Brotherhood)
    run_check(
        "5. Anime Detail (FMAB: 5114)",
        "GET",
        "/api/anime/5114",
        validate_fn=lambda d: None if "Fullmetal" in d.get("name", "") else f"Unexpected anime name: {d.get('name')}",
    )

    # 6. Search Autocomplete
    run_check(
        "6. Search Autocomplete ('hunter')",
        "GET",
        "/api/anime/search?q=hunter&limit=3",
        validate_fn=lambda d: None if len(d) > 0 and any("Hunter" in item.get("name", "") for item in d) else "No matching items for query 'hunter'",
    )

    # 7. Content-Based Recommendations (Death Note)
    run_check(
        "7. Content-Based Similar Anime (Death Note: 1535)",
        "GET",
        "/api/anime/1535/similar?top_n=3",
        validate_fn=lambda d: None if len(d.get("recommendations", [])) == 3 else f"Expected 3 recommendations, got {len(d.get('recommendations', []))}",
    )

    # 8. Popularity Baseline Recommendations
    run_check(
        "8. Popularity Quality Baseline",
        "GET",
        "/api/recommendations/popular?top_n=5",
        validate_fn=lambda d: None if len(d.get("recommendations", [])) == 5 else f"Expected 5 recommendations, got {len(d.get('recommendations', []))}",
    )

    # 9. Personalized Recommendations for Demo User 1 (Warm Profile)
    run_check(
        "9. Personalized Recs (User 1 - Warm)",
        "GET",
        "/api/recommendations/personalized?top_n=4",
        headers={"X-User-Id": "1"},
        validate_fn=lambda d: None if len(d.get("recommendations", [])) == 4 else f"Expected 4 recommendations, got {len(d.get('recommendations', []))}",
    )

    # 10. Cold-Start Recommendations for User 2 (Fresh Profile)
    run_check(
        "10. Cold-Start Recs (User 2 - Fresh)",
        "GET",
        "/api/recommendations/personalized?top_n=4",
        headers={"X-User-Id": "2"},
        validate_fn=lambda d: None if len(d.get("recommendations", [])) == 4 else f"Expected 4 recommendations, got {len(d.get('recommendations', []))}",
    )

    # 11. Read-Only Watchlist Query
    run_check(
        "11. Watchlist Query (User 1)",
        "GET",
        "/api/watchlist",
        headers={"X-User-Id": "1"},
        validate_fn=lambda d: None if isinstance(d, list) else "Expected list of watchlist items",
    )

    # 12. Read-Only Ratings Query
    run_check(
        "12. Ratings Query (User 1)",
        "GET",
        "/api/ratings",
        headers={"X-User-Id": "1"},
        validate_fn=lambda d: None if isinstance(d, list) else "Expected list of ratings",
    )

    if standalone:
        print(f"\n-----------------------------------------------------------")
        print(f"SMOKE TEST SUMMARY: {passed} PASSED, {failed} FAILED (Total: {passed + failed})")
        print(f"Mode: {'FastAPI TestClient (in-process)' if using_test_client else f'Live HTTP ({target_url})'}")
        print(f"-----------------------------------------------------------")
        if failed > 0:
            print("[RESULT] SMOKE TEST FAILED")
        else:
            print("[RESULT] ALL PRODUCTION CONTRACTS VERIFIED OPERATIONAL!")

    return failed


def test_smoke_endpoints():
    """Pytest test hook verifying smoke endpoints."""
    failed = run_smoke_tests(standalone=False)
    assert failed == 0, f"{failed} smoke test checks failed"


if __name__ == "__main__":
    failed_count = run_smoke_tests(standalone=True)
    sys.exit(1 if failed_count > 0 else 0)
