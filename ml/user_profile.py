"""
User Preference Modeling using Rocchio vector profile generation.
Supports positive preference signals (likes / high ratings) and negative
signals (dislikes / low ratings) to produce personalized taste vectors.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, issparse

from ml.config import (
    NEGATIVE_RATING_THRESHOLD,
    POSITIVE_RATING_THRESHOLD,
    ROCCHIO_ALPHA,
    ROCCHIO_BETA,
)
from ml.utils import setup_logger

logger = setup_logger("UserProfile")


class UserProfileRecommender:
    """
    Builds personalized user preference profiles in TF-IDF space and
    computes recommendation rankings across the catalog.
    """

    def __init__(
        self,
        anime_df: pd.DataFrame,
        tfidf_matrix: Union[csr_matrix, np.ndarray],
        alpha: float = ROCCHIO_ALPHA,
        beta: float = ROCCHIO_BETA,
        pos_threshold: float = POSITIVE_RATING_THRESHOLD,
        neg_threshold: float = NEGATIVE_RATING_THRESHOLD,
    ):
        self.df = anime_df.reset_index(drop=True)
        self.tfidf_matrix = tfidf_matrix if issparse(tfidf_matrix) else csr_matrix(tfidf_matrix)
        self.alpha = alpha
        self.beta = beta
        self.pos_threshold = pos_threshold
        self.neg_threshold = neg_threshold

        self._mal_id_to_idx: Dict[int, int] = {
            int(mal_id): idx for idx, mal_id in enumerate(self.df["mal_id"])
        }

    def build_user_vector(
        self,
        user_history: Optional[List[Dict[str, Any]]] = None,
        liked_ids: Optional[List[int]] = None,
        disliked_ids: Optional[List[int]] = None,
    ) -> np.ndarray:
        """
        Constructs a normalized user preference vector using the Rocchio formula:
            u = alpha * (1 / |P|) * sum(w_i * v_i) - beta * (1 / |N|) * sum(w_j * v_j)
            
        Args:
            user_history: List of dicts with 'mal_id' (or 'anime_id') and 'rating' (1-10 float).
            liked_ids: Explicit list of positive anime MAL IDs.
            disliked_ids: Explicit list of negative anime MAL IDs.
            
        Returns:
            Normalized 1D numpy array user vector matching the TF-IDF feature dimension.
        """
        num_features = self.tfidf_matrix.shape[1]
        pos_indices: List[int] = []
        pos_weights: List[float] = []
        neg_indices: List[int] = []
        neg_weights: List[float] = []

        # 1. Parse structured rating history if provided
        if user_history:
            for item in user_history:
                anime_id = int(item.get("mal_id", item.get("anime_id", -1)))
                if anime_id not in self._mal_id_to_idx:
                    continue
                idx = self._mal_id_to_idx[anime_id]
                rating = float(item.get("rating", 7.0))

                if rating >= self.pos_threshold:
                    weight = max(0.1, (rating - (self.pos_threshold - 1.0)))
                    pos_indices.append(idx)
                    pos_weights.append(weight)
                elif rating <= self.neg_threshold:
                    weight = max(0.1, (self.neg_threshold + 1.0 - rating))
                    neg_indices.append(idx)
                    neg_weights.append(weight)
                else:
                    # Neutral rating, moderate positive signal
                    pos_indices.append(idx)
                    pos_weights.append(0.5)

        # 2. Add explicit liked IDs
        if liked_ids:
            for mal_id in liked_ids:
                if mal_id in self._mal_id_to_idx:
                    idx = self._mal_id_to_idx[mal_id]
                    if idx not in pos_indices:
                        pos_indices.append(idx)
                        pos_weights.append(1.0)

        # 3. Add explicit disliked IDs
        if disliked_ids:
            for mal_id in disliked_ids:
                if mal_id in self._mal_id_to_idx:
                    idx = self._mal_id_to_idx[mal_id]
                    if idx not in neg_indices:
                        neg_indices.append(idx)
                        neg_weights.append(1.0)

        # If no valid indices found, return zero vector
        if not pos_indices and not neg_indices:
            return np.zeros(num_features, dtype=np.float32)

        # Build positive centroid
        pos_vec = np.zeros(num_features, dtype=np.float32)
        if pos_indices:
            total_pos_weight = sum(pos_weights)
            for idx, w in zip(pos_indices, pos_weights):
                vec = self.tfidf_matrix[idx].toarray().ravel()
                pos_vec += (w / total_pos_weight) * vec

        # Build negative centroid
        neg_vec = np.zeros(num_features, dtype=np.float32)
        if neg_indices:
            total_neg_weight = sum(neg_weights)
            for idx, w in zip(neg_indices, neg_weights):
                vec = self.tfidf_matrix[idx].toarray().ravel()
                neg_vec += (w / total_neg_weight) * vec

        # Rocchio combination: alpha * positive - beta * negative
        user_vec = (self.alpha * pos_vec) - (self.beta * neg_vec)

        # Zero out negative components (standard Rocchio retrieval)
        user_vec = np.maximum(user_vec, 0.0)

        # L2 Normalize
        norm = np.linalg.norm(user_vec)
        if norm > 0:
            user_vec = user_vec / norm

        return user_vec

    def get_user_similarity_vector(
        self,
        user_history: Optional[List[Dict[str, Any]]] = None,
        liked_ids: Optional[List[int]] = None,
        disliked_ids: Optional[List[int]] = None,
    ) -> np.ndarray:
        """
        Computes cosine similarity of the user taste vector against all catalog items.
        """
        user_vec = self.build_user_vector(user_history, liked_ids, disliked_ids)
        if np.linalg.norm(user_vec) == 0:
            return np.zeros(len(self.df), dtype=np.float32)

        sims = self.tfidf_matrix.dot(user_vec).ravel()
        return sims

    def recommend(
        self,
        user_history: Optional[List[Dict[str, Any]]] = None,
        liked_ids: Optional[List[int]] = None,
        disliked_ids: Optional[List[int]] = None,
        top_n: int = 10,
        exclude_seen: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generates Top-N recommendations tailored to the user's preference profile.
        """
        if top_n <= 0:
            return []

        # Identify all seen anime IDs to exclude
        seen_ids = set()
        if exclude_seen:
            if user_history:
                for item in user_history:
                    seen_ids.add(int(item.get("mal_id", item.get("anime_id", -1))))
            if liked_ids:
                seen_ids.update(liked_ids)
            if disliked_ids:
                seen_ids.update(disliked_ids)

        sims = self.get_user_similarity_vector(user_history, liked_ids, disliked_ids).copy()

        # If user vector was empty, return empty list (signaling cold start required)
        if np.max(sims) == 0.0:
            logger.info("User vector has zero norm. Cold start fallback needed.")
            return []

        # Mask seen items
        for seen_id in seen_ids:
            if seen_id in self._mal_id_to_idx:
                sims[self._mal_id_to_idx[seen_id]] = -1.0

        top_indices = np.argpartition(sims, -top_n)[-top_n:]
        top_indices = top_indices[np.argsort(-sims[top_indices])]

        recommendations = []
        for rank, rec_idx in enumerate(top_indices, 1):
            row = self.df.iloc[rec_idx]
            sim_score = float(sims[rec_idx])
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
                "user_similarity_score": round(sim_score, 4),
                "img_url": str(row.get("img_url", "")),
            }
            recommendations.append(rec_item)

        return recommendations
