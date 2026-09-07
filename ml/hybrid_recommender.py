"""
Configurable Hybrid Anime Recommendation Engine.
Blends content similarity, user taste profiling, and Bayesian popularity
with customizable weighting and cold-start fallback integration.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from ml.cold_start import ColdStartHandler
from ml.config import DEFAULT_FEED_WEIGHTS, DEFAULT_HYBRID_WEIGHTS
from ml.content_recommender import ContentRecommender
from ml.popularity_recommender import PopularityRecommender
from ml.user_profile import UserProfileRecommender
from ml.utils import setup_logger

logger = setup_logger("HybridRecommender")


class HybridRecommender:
    """
    Combines Content Similarity, User Taste Profile, and Bayesian Popularity
    into a unified ranking with configurable linear weighting:
        Score = w_content * S_content + w_user * S_user + w_pop * S_pop
    """

    def __init__(
        self,
        anime_df: pd.DataFrame,
        content_model: ContentRecommender,
        popularity_model: PopularityRecommender,
        user_profile_model: UserProfileRecommender,
        cold_start_handler: Optional[ColdStartHandler] = None,
        default_weights: Optional[Dict[str, float]] = None,
    ):
        self.df = anime_df.reset_index(drop=True)
        self.content_model = content_model
        self.popularity_model = popularity_model
        self.user_profile_model = user_profile_model
        self.cold_start_handler = cold_start_handler or ColdStartHandler(self.df, self.popularity_model)
        self.default_weights = default_weights or DEFAULT_HYBRID_WEIGHTS

        self._mal_id_to_idx: Dict[int, int] = {
            int(mal_id): idx for idx, mal_id in enumerate(self.df["mal_id"])
        }

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Ensures weights sum to 1.0 and contain all three components."""
        w_c = max(0.0, float(weights.get("content", 0.0)))
        w_u = max(0.0, float(weights.get("user", 0.0)))
        w_p = max(0.0, float(weights.get("popularity", 0.0)))

        total = w_c + w_u + w_p
        if total == 0:
            return {"content": 0.5, "user": 0.3, "popularity": 0.2}

        return {
            "content": w_c / total,
            "user": w_u / total,
            "popularity": w_p / total,
        }

    def recommend(
        self,
        query_anime: Optional[Union[str, int]] = None,
        user_history: Optional[List[Dict[str, Any]]] = None,
        liked_ids: Optional[List[int]] = None,
        disliked_ids: Optional[List[int]] = None,
        selected_genres: Optional[Union[str, List[str]]] = None,
        weights: Optional[Dict[str, float]] = None,
        top_n: int = 10,
        anime_type: Optional[str] = None,
        exclude_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates hybrid recommendations blending content, user taste, and popularity.
        
        Args:
            query_anime: Title (str) or MAL ID (int) of currently viewed anime (optional).
            user_history: User rating history list of dicts (optional).
            liked_ids: Explicit list of liked anime MAL IDs (optional).
            disliked_ids: Explicit list of disliked anime MAL IDs (optional).
            selected_genres: List of genres for cold-start fallback (optional).
            weights: Dictionary with 'content', 'user', 'popularity' weight multipliers.
            top_n: Number of recommendations to retrieve.
            anime_type: Format filter ('TV', 'Movie', etc.).
            exclude_ids: Explicit list of MAL IDs to exclude.
            
        Returns:
            Ranked list of recommendation dictionaries.
        """
        if top_n <= 0:
            return []

        # Track IDs to exclude
        all_exclude_ids = set(exclude_ids or [])
        has_query_anime = False
        query_idx: Optional[int] = None

        # 1. Content Signal
        s_content = np.zeros(len(self.df), dtype=np.float32)
        if query_anime is not None and str(query_anime).strip():
            try:
                query_idx, q_row = self.content_model.find_anime_index(query_anime)
                s_content = self.content_model.get_similarity_vector(query_anime)
                all_exclude_ids.add(int(q_row["mal_id"]))
                has_query_anime = True
            except ValueError as e:
                logger.warning(f"Query anime '{query_anime}' not resolved: {e}. Omitting content signal.")

        # 2. User Preference Signal
        s_user = np.zeros(len(self.df), dtype=np.float32)
        has_user_profile = bool(user_history or liked_ids or disliked_ids)
        if has_user_profile:
            s_user = self.user_profile_model.get_user_similarity_vector(
                user_history=user_history, liked_ids=liked_ids, disliked_ids=disliked_ids
            )
            # Add user history to exclusions
            if user_history:
                for item in user_history:
                    all_exclude_ids.add(int(item.get("mal_id", item.get("anime_id", -1))))
            if liked_ids:
                all_exclude_ids.update(liked_ids)
            if disliked_ids:
                all_exclude_ids.update(disliked_ids)

        # Cold-Start Check: If neither query anime nor user profile exists
        if not has_query_anime and not has_user_profile:
            logger.info("Neither query anime nor user profile provided. Invoking cold-start handler.")
            return self.cold_start_handler.recommend(
                selected_genres=selected_genres, anime_type=anime_type, top_n=top_n
            )

        # 3. Popularity / Baseline Signal
        s_pop = self.popularity_model.get_baseline_scores()

        # Determine effective weights
        if weights:
            eff_weights = self._normalize_weights(weights)
        elif has_query_anime and has_user_profile:
            eff_weights = self._normalize_weights(self.default_weights)
        elif has_query_anime and not has_user_profile:
            # Item-to-item hybrid: 75% content similarity, 25% quality/popularity
            eff_weights = {"content": 0.75, "user": 0.0, "popularity": 0.25}
        else:
            # Personalized feed: 70% user taste, 30% quality/popularity
            eff_weights = self._normalize_weights(DEFAULT_FEED_WEIGHTS)

        # Normalize component vectors to [0, 1] range before combining
        def norm_vec(v: np.ndarray) -> np.ndarray:
            v_max = float(np.max(v)) if len(v) > 0 else 0.0
            return v / v_max if v_max > 0 else v

        s_content_norm = norm_vec(s_content)
        s_user_norm = norm_vec(s_user)
        s_pop_norm = norm_vec(s_pop)

        # Linear combination
        hybrid_scores = (
            eff_weights["content"] * s_content_norm
            + eff_weights["user"] * s_user_norm
            + eff_weights["popularity"] * s_pop_norm
        )

        # Apply exclusions
        for ex_id in all_exclude_ids:
            if ex_id in self._mal_id_to_idx:
                hybrid_scores[self._mal_id_to_idx[ex_id]] = -1.0

        # Apply type filter if requested
        if anime_type and str(anime_type).strip().lower() != "all":
            type_mask = self.df["type"].str.lower() != str(anime_type).strip().lower()
            hybrid_scores[type_mask] = -1.0

        top_indices = np.argpartition(hybrid_scores, -top_n)[-top_n:]
        top_indices = top_indices[np.argsort(-hybrid_scores[top_indices])]

        recommendations = []
        for rank, rec_idx in enumerate(top_indices, 1):
            row = self.df.iloc[rec_idx]
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
                "hybrid_score": round(float(hybrid_scores[rec_idx]), 4),
                "content_score": round(float(s_content_norm[rec_idx]), 4),
                "user_score": round(float(s_user_norm[rec_idx]), 4),
                "popularity_score": round(float(s_pop_norm[rec_idx]), 4),
                "weights_used": eff_weights,
                "img_url": str(row.get("img_url", "")),
            }
            recommendations.append(rec_item)

        return recommendations
