"""
Cold-Start Recommendation Handler.
Provides graceful fallbacks for new users with no history:
- Tier 1: Genre-conditioned recommendations if user selects preferred genres
- Tier 2: Diverse, high-quality Bayesian baseline recommendations
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from ml.popularity_recommender import PopularityRecommender
from ml.utils import setup_logger

logger = setup_logger("ColdStart")


class ColdStartHandler:
    """
    Handles cold-start scenarios when user interaction history is absent or sparse.
    """

    def __init__(self, anime_df: pd.DataFrame, popularity_model: PopularityRecommender):
        self.df = anime_df.reset_index(drop=True)
        self.popularity_model = popularity_model

    def recommend_from_genres(
        self,
        selected_genres: Union[str, List[str]],
        anime_type: Optional[str] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generates cold-start recommendations conditioned on user-selected genres.
        Combines genre overlap with Bayesian quality baseline.
        """
        if isinstance(selected_genres, str):
            genres_list = [g.strip().lower() for g in selected_genres.split(",") if g.strip()]
        else:
            genres_list = [str(g).strip().lower() for g in selected_genres if str(g).strip()]

        if not genres_list:
            return self.recommend_popular_diverse(anime_type=anime_type, top_n=top_n)

        # Calculate genre overlap count for each anime
        def compute_overlap(anime_genres: str) -> float:
            if not isinstance(anime_genres, str):
                return 0.0
            a_lower = anime_genres.lower()
            return sum(1.0 for g in genres_list if g in a_lower)

        overlaps = self.df["genres"].apply(compute_overlap).values
        baseline = self.popularity_model.get_baseline_scores()

        # Composite score: 60% genre overlap match, 40% quality/popularity baseline
        max_overlap = max(1.0, float(np.max(overlaps)))
        overlap_norm = overlaps / max_overlap
        cold_score = (0.60 * overlap_norm + 0.40 * baseline)

        temp_df = self.df.copy()
        temp_df["cold_score"] = cold_score

        mask = overlaps > 0
        if anime_type and str(anime_type).strip().lower() != "all":
            mask &= temp_df["type"].str.lower() == str(anime_type).strip().lower()

        filtered_df = temp_df[mask].sort_values(by="cold_score", ascending=False).head(top_n)

        # If not enough matches, backfill from popular baseline
        if len(filtered_df) < top_n:
            needed = top_n - len(filtered_df)
            existing_ids = set(filtered_df["mal_id"])
            fallback = self.popularity_model.recommend(top_n=needed, anime_type=anime_type, exclude_ids=list(existing_ids))
            for item in fallback:
                item["cold_score"] = item.get("baseline_score", 0.5)

        recommendations = []
        for rank, (_, row) in enumerate(filtered_df.iterrows(), 1):
            rec_item = {
                "rank": rank,
                "mal_id": int(row["mal_id"]),
                "name": str(row["name"]),
                "english_name": str(row.get("english_name", "Unknown")),
                "genres": str(row.get("genres", "")),
                "type": str(row.get("type", "Unknown")),
                "score": float(row["score"]) if pd.notna(row.get("score")) else None,
                "weighted_score": float(row.get("weighted_score", 0.0)),
                "members": int(row.get("members", 0)),
                "release_year": int(row["release_year"]) if pd.notna(row.get("release_year")) else None,
                "cold_score": round(float(row["cold_score"]), 4),
                "img_url": str(row.get("img_url", "")),
            }
            recommendations.append(rec_item)

        return recommendations

    def recommend_popular_diverse(
        self,
        anime_type: Optional[str] = None,
        top_n: int = 10,
        max_per_primary_genre: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Global cold-start fallback when zero user information is known.
        Returns top-tier anime while enforcing primary genre diversity.
        """
        candidates = self.popularity_model.recommend(top_n=top_n * 3, anime_type=anime_type)

        selected = []
        genre_tally: Dict[str, int] = {}

        for item in candidates:
            # Check primary genre diversity
            first_genre = item.get("genres", "Unknown").split(",")[0].strip() if item.get("genres") else "Unknown"
            count = genre_tally.get(first_genre, 0)
            if count < max_per_primary_genre or len(selected) + (len(candidates) - len(selected)) <= top_n:
                selected.append(item)
                genre_tally[first_genre] = count + 1
            if len(selected) >= top_n:
                break

        # Re-assign ranks 1..top_n
        for idx, item in enumerate(selected, 1):
            item["rank"] = idx

        return selected

    def recommend(
        self,
        selected_genres: Optional[Union[str, List[str]]] = None,
        anime_type: Optional[str] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """Unified cold-start recommendation method."""
        if selected_genres:
            return self.recommend_from_genres(selected_genres, anime_type=anime_type, top_n=top_n)
        return self.recommend_popular_diverse(anime_type=anime_type, top_n=top_n)
