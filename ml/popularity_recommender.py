"""
Popularity and Bayesian Quality Baseline Recommender.
Provides non-personalized baseline rankings, genre/type filtering, and
baseline scoring vectors for model comparison and hybrid blending.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from ml.utils import setup_logger

logger = setup_logger("PopularityRecommender")


class PopularityRecommender:
    """
    Baseline recommender ranking anime by a balanced composite of
    Bayesian regularized score (quality signal) and log-transformed members (popularity signal).
    """

    def __init__(self, anime_df: pd.DataFrame):
        self.df = anime_df.reset_index(drop=True).copy()

        # Compute normalized baseline scores once at initialization
        self._compute_baseline_scores()

    def _compute_baseline_scores(self) -> None:
        """Computes composite popularity + Bayesian quality score on [0, 1] scale."""
        # 1. Weighted score component
        w_score = self.df["weighted_score"].fillna(self.df["weighted_score"].mean()).astype(float)
        w_min = float(w_score.min())
        w_max = float(w_score.max())
        w_norm = (w_score - w_min) / (w_max - w_min) if w_max > w_min else np.zeros_like(w_score)

        # 2. Log members component
        log_m = self.df["log_members"].fillna(0.0).astype(float)
        m_min = float(log_m.min())
        m_max = float(log_m.max())
        m_norm = (log_m - m_min) / (m_max - m_min) if m_max > m_min else np.zeros_like(log_m)

        # Composite baseline score: 70% quality, 30% community popularity
        self.baseline_scores = (0.70 * w_norm + 0.30 * m_norm).values.round(4)
        self.df["baseline_score"] = self.baseline_scores

    def get_baseline_scores(self) -> np.ndarray:
        """Returns the 1D array of normalized baseline scores for the entire catalog."""
        return self.baseline_scores

    def recommend(
        self,
        top_n: int = 10,
        genre: Optional[Union[str, List[str]]] = None,
        anime_type: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        exclude_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates Top-N popularity/quality baseline recommendations with optional filtering.
        
        Args:
            top_n: Number of recommendations to return.
            genre: Single genre string or list of genres to filter by.
            anime_type: Production format ('TV', 'Movie', 'OVA', etc.).
            min_year: Earliest release year (inclusive).
            max_year: Latest release year (inclusive).
            exclude_ids: List of MAL IDs to exclude from results.
            
        Returns:
            List of dictionaries containing recommended anime metadata.
        """
        if top_n <= 0:
            return []

        mask = pd.Series(True, index=self.df.index)

        # Exclude IDs
        if exclude_ids:
            mask &= ~self.df["mal_id"].isin(exclude_ids)

        # Filter by genre
        if genre:
            if isinstance(genre, str):
                genres_to_match = [g.strip().lower() for g in genre.split(",") if g.strip()]
            else:
                genres_to_match = [str(g).strip().lower() for g in genre if str(g).strip()]

            if genres_to_match:
                genre_mask = self.df["genres"].fillna("").str.lower().apply(
                    lambda g_str: all(req in g_str for req in genres_to_match)
                )
                mask &= genre_mask

        # Filter by type
        if anime_type and str(anime_type).strip().lower() != "all":
            mask &= self.df["type"].str.lower() == str(anime_type).strip().lower()

        # Filter by release year
        if min_year is not None:
            mask &= self.df["release_year"].fillna(-1) >= min_year
        if max_year is not None:
            mask &= self.df["release_year"].fillna(9999) <= max_year

        filtered_df = self.df[mask].sort_values(by="baseline_score", ascending=False).head(top_n)

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
                "baseline_score": float(row.get("baseline_score", 0.0)),
                "img_url": str(row.get("img_url", "")),
            }
            recommendations.append(rec_item)

        return recommendations
