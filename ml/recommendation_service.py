"""
Unified High-Level Recommendation Service for ANIMORA.
Loads persisted artifacts and exposes a clean, cohesive interface for
content-based, user profile, baseline popularity, cold-start, and hybrid recommendations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import difflib
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from ml.cold_start import ColdStartHandler
from ml.config import (
    ANIME_INDEX_PATH,
    MODEL_METADATA_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
)
from ml.content_recommender import ContentRecommender
from ml.hybrid_recommender import HybridRecommender
from ml.popularity_recommender import PopularityRecommender
from ml.train import train_and_persist_models
from ml.user_profile import UserProfileRecommender
from ml.utils import load_json, setup_logger

logger = setup_logger("RecommendationService")


class RecommendationService:
    """
    Production-ready facade providing all recommendation capabilities.
    Initializes from saved artifacts for near-instant (<150ms) startup time.
    """

    def __init__(self, auto_train: bool = True):
        self._load_or_train_artifacts(auto_train=auto_train)
        self._init_models()

    def _load_or_train_artifacts(self, auto_train: bool = True) -> None:
        """Loads serialized model files, or runs training if artifacts are missing."""
        required_paths = [TFIDF_VECTORIZER_PATH, TFIDF_MATRIX_PATH, ANIME_INDEX_PATH]
        missing = [p for p in required_paths if not p.exists() or p.stat().st_size == 0]

        if missing:
            if auto_train:
                logger.info(f"Missing artifacts ({[p.name for p in missing]}). Initiating training...")
                train_and_persist_models()
            else:
                raise FileNotFoundError(f"Missing model artifacts: {[p.name for p in missing]}. Run ml.train first.")

        try:
            logger.info("Loading persisted model artifacts from disk...")
            self.vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
            self.tfidf_matrix = load_npz(TFIDF_MATRIX_PATH)
            self.anime_df = pd.read_parquet(ANIME_INDEX_PATH)
        except Exception as exc:
            err_msg = (
                f"ANIMORA ML Startup Failure: Failed to load precomputed model artifacts from '{TFIDF_MATRIX_PATH.parent}'. "
                f"Ensure 'tfidf_matrix.npz', 'tfidf_vectorizer.joblib', and 'anime_index.parquet' are present and uncorrupted. "
                f"Root cause: {exc}"
            )
            logger.critical(err_msg)
            raise RuntimeError(err_msg) from exc
        
        self.metadata = {}
        if MODEL_METADATA_PATH.exists():
            try:
                self.metadata = load_json(MODEL_METADATA_PATH)
            except Exception as e:
                logger.warning(f"Could not read model metadata: {e}")

        logger.info(
            f"RecommendationService initialized with {len(self.anime_df):,} anime titles "
            f"and {self.tfidf_matrix.shape[1]:,} features."
        )

    def _init_models(self) -> None:
        """Instantiates all recommendation engine components."""
        self.content_model = ContentRecommender(self.anime_df, self.tfidf_matrix, self.vectorizer)
        self.popularity_model = PopularityRecommender(self.anime_df)
        self.user_profile_model = UserProfileRecommender(self.anime_df, self.tfidf_matrix)
        self.cold_start_handler = ColdStartHandler(self.anime_df, self.popularity_model)
        self.hybrid_model = HybridRecommender(
            anime_df=self.anime_df,
            content_model=self.content_model,
            popularity_model=self.popularity_model,
            user_profile_model=self.user_profile_model,
            cold_start_handler=self.cold_start_handler,
        )

    # -------------------------------------------------------------------------
    # Public Recommendation APIs
    # -------------------------------------------------------------------------

    def get_content_recommendations(
        self,
        query: Union[str, int],
        top_n: int = 10,
        exclude_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Content-based recommendations for a specific anime title or MAL ID."""
        return self.content_model.recommend(query=query, top_n=top_n, exclude_ids=exclude_ids)

    def get_popular_recommendations(
        self,
        genre: Optional[Union[str, List[str]]] = None,
        anime_type: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        top_n: int = 10,
        exclude_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Popularity and Bayesian baseline recommendations with optional filtering."""
        return self.popularity_model.recommend(
            top_n=top_n,
            genre=genre,
            anime_type=anime_type,
            min_year=min_year,
            max_year=max_year,
            exclude_ids=exclude_ids,
        )

    def get_user_recommendations(
        self,
        user_history: Optional[List[Dict[str, Any]]] = None,
        liked_ids: Optional[List[int]] = None,
        disliked_ids: Optional[List[int]] = None,
        top_n: int = 10,
        exclude_seen: bool = True,
    ) -> List[Dict[str, Any]]:
        """Personalized recommendations matching a user's rated profile vector."""
        recs = self.user_profile_model.recommend(
            user_history=user_history,
            liked_ids=liked_ids,
            disliked_ids=disliked_ids,
            top_n=top_n,
            exclude_seen=exclude_seen,
        )
        if not recs:
            # Fall back to cold start if profile had no positive signal
            return self.get_cold_start_recommendations(top_n=top_n)
        return recs

    def get_hybrid_recommendations(
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
        """Configurable hybrid recommendations combining content, user taste, and popularity."""
        return self.hybrid_model.recommend(
            query_anime=query_anime,
            user_history=user_history,
            liked_ids=liked_ids,
            disliked_ids=disliked_ids,
            selected_genres=selected_genres,
            weights=weights,
            top_n=top_n,
            anime_type=anime_type,
            exclude_ids=exclude_ids,
        )

    def get_cold_start_recommendations(
        self,
        selected_genres: Optional[Union[str, List[str]]] = None,
        anime_type: Optional[str] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """Cold-start recommendations for new users with sparse or zero history."""
        return self.cold_start_handler.recommend(
            selected_genres=selected_genres, anime_type=anime_type, top_n=top_n
        )

    def search_anime(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for anime titles using prefix, substring, and fuzzy matching.
        """
        clean_q = str(query).strip().lower()
        if not clean_q:
            return []

        results = []
        seen_ids = set()

        # 1. Exact or prefix matches
        for idx, row in self.anime_df.iterrows():
            name = str(row["name"]).strip()
            eng = str(row.get("english_name", "")).strip()
            if name.lower().startswith(clean_q) or eng.lower().startswith(clean_q):
                if row["mal_id"] not in seen_ids:
                    seen_ids.add(row["mal_id"])
                    results.append(self._row_to_summary(row))
            if len(results) >= limit:
                return results

        # 2. Substring matches
        for idx, row in self.anime_df.iterrows():
            name = str(row["name"]).strip()
            eng = str(row.get("english_name", "")).strip()
            if clean_q in name.lower() or clean_q in eng.lower():
                if row["mal_id"] not in seen_ids:
                    seen_ids.add(row["mal_id"])
                    results.append(self._row_to_summary(row))
            if len(results) >= limit:
                return results

        # 3. Fuzzy matches
        all_titles = list(self.anime_df["name"].dropna())
        close = difflib.get_close_matches(clean_q, [t.lower() for t in all_titles], n=limit, cutoff=0.5)
        for c in close:
            matches = self.anime_df[self.anime_df["name"].str.lower() == c]
            for _, row in matches.iterrows():
                if row["mal_id"] not in seen_ids:
                    seen_ids.add(row["mal_id"])
                    results.append(self._row_to_summary(row))
                if len(results) >= limit:
                    return results

        return results

    def _row_to_summary(self, row: pd.Series) -> Dict[str, Any]:
        """Formats a series into a clean summary dict."""
        return {
            "mal_id": int(row["mal_id"]),
            "name": str(row["name"]),
            "english_name": str(row.get("english_name", "Unknown")),
            "genres": str(row.get("genres", "")),
            "type": str(row.get("type", "Unknown")),
            "score": float(row["score"]) if pd.notna(row.get("score")) else None,
            "weighted_score": float(row.get("weighted_score", 0.0)),
            "members": int(row.get("members", 0)),
            "release_year": int(row["release_year"]) if pd.notna(row.get("release_year")) else None,
            "img_url": str(row.get("img_url", "")),
        }
