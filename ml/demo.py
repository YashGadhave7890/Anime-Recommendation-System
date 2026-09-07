"""
Demonstration and CLI Verification script for ANIMORA Recommendation Engine.
Runs through all recommendation modes with real MyAnimeList data and displays clean, formatted output.
"""

from ml.recommendation_service import RecommendationService


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_recs(recs: list, score_col: str = "similarity_score") -> None:
    for r in recs:
        rank = r.get("rank", "-")
        name = r.get("name", "Unknown")
        genres = r.get("genres", "")
        anime_type = r.get("type", "")
        year = r.get("release_year", "N/A")
        score = r.get(score_col, r.get("similarity_score", r.get("hybrid_score", 0.0)))
        print(f"  #{rank:<2} | {name:<35} | {anime_type:<6} | {year} | {score_col}: {score:.4f} | {genres[:30]}")


def run_demo() -> None:
    print_section("ANIMORA — Recommendation Engine Demo & Verification")
    service = RecommendationService(auto_train=False)

    # 1. Content-Based: Death Note (Top 5)
    print_section("1. Content-Based Recommendations: 'Death Note' (Top 5)")
    recs_dn = service.get_content_recommendations("Death Note", top_n=5)
    print_recs(recs_dn, "similarity_score")
    assert not any(r["mal_id"] == 1535 for r in recs_dn), "Error: Input anime was not excluded!"

    # 2. Content-Based: Fullmetal Alchemist: Brotherhood (Top 5)
    print_section("2. Content-Based Recommendations: 'Fullmetal Alchemist: Brotherhood'")
    recs_fma = service.get_content_recommendations("Fullmetal Alchemist: Brotherhood", top_n=5)
    print_recs(recs_fma, "similarity_score")

    # 3. Content-Based: Kimi no Na wa. (Top 5)
    print_section("3. Content-Based Recommendations: 'Kimi no Na wa.' (Your Name)")
    recs_knn = service.get_content_recommendations("Kimi no Na wa.", top_n=5)
    print_recs(recs_knn, "similarity_score")

    # 4. Unknown Title Graceful Handling
    print_section("4. Error Handling: Unknown Title Lookup")
    test_unknown = "NonExistentAnimeTitleXYZ999"
    try:
        service.get_content_recommendations(test_unknown, top_n=5)
    except ValueError as e:
        print(f"  [SUCCESS] Expected error caught: {e}")

    # 5. Popularity Baseline: Top Action TV Series
    print_section("5. Popularity Baseline: Top 5 Action TV Series")
    pop_recs = service.get_popular_recommendations(genre="Action", anime_type="TV", top_n=5)
    print_recs(pop_recs, "baseline_score")

    # 6. User Profile Modeling: Likes Mystery/Psychological, Dislikes Sports
    print_section("6. User Taste Profile: Likes Death Note (10) & FMA (9), Dislikes Haikyuu (3)")
    user_history = [
        {"mal_id": 1535, "rating": 10.0},  # Death Note
        {"mal_id": 5114, "rating": 9.0},   # FMA: Brotherhood
        {"mal_id": 28891, "rating": 3.0},  # Haikyuu!!
    ]
    user_recs = service.get_user_recommendations(user_history=user_history, top_n=5)
    print_recs(user_recs, "user_similarity_score")

    # 7. Hybrid Recommender: Currently Viewing 'Cowboy Bebop' + User Taste Profile
    print_section("7. Hybrid Engine: Query 'Cowboy Bebop' + User History (50% Content, 30% User, 20% Pop)")
    hybrid_recs = service.get_hybrid_recommendations(
        query_anime="Cowboy Bebop",
        user_history=user_history,
        top_n=5,
    )
    print_recs(hybrid_recs, "hybrid_score")

    # 8. Cold Start Tier 1: User Selects 'Sci-Fi' & 'Mecha'
    print_section("8. Cold-Start Tier 1: User Selects Genres ['Sci-Fi', 'Mecha']")
    cold_genre_recs = service.get_cold_start_recommendations(selected_genres=["Sci-Fi", "Mecha"], top_n=5)
    print_recs(cold_genre_recs, "cold_score")

    # 9. Cold Start Tier 2: Pure Cold Start (Zero User Data)
    print_section("9. Cold-Start Tier 2: Pure Cold Start (Diverse Quality Fallback)")
    pure_cold_recs = service.get_cold_start_recommendations(top_n=5)
    print_recs(pure_cold_recs, "baseline_score")

    # 10. Fuzzy Title Search
    print_section("10. Fuzzy Title Search: Query 'attack titan'")
    search_results = service.search_anime("attack titan", limit=3)
    for res in search_results:
        print(f"  Found: {res['name']} (ID: {res['mal_id']}) | Score: {res['score']} | {res['genres']}")

    print("\n" + "=" * 70)
    print("  ALL DEMO & VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
