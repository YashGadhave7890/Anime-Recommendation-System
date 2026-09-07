"""
Content-based Anime Recommender using TF-IDF and Cosine Similarity.
Provides exact and fuzzy title matching, similarity scoring, and top-N retrieval.
"""

import difflib
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, issparse
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.utils import setup_logger

logger = setup_logger("ContentRecommender")


class ContentRecommender:
    """
    Content-Based Recommender utilizing TF-IDF vectors of anime content soup
    and sparse cosine similarity dot products.
    """

    def __init__(
        self,
        anime_df: pd.DataFrame,
        tfidf_matrix: Union[csr_matrix, np.ndarray],
        vectorizer: Optional[TfidfVectorizer] = None,
    ):
        self.df = anime_df.reset_index(drop=True)
        self.tfidf_matrix = tfidf_matrix if issparse(tfidf_matrix) else csr_matrix(tfidf_matrix)
        self.vectorizer = vectorizer

        # Pre-build lookup dictionaries for fast O(1) searches
        self._mal_id_to_idx: Dict[int, int] = {
            int(mal_id): idx for idx, mal_id in enumerate(self.df["mal_id"])
        }
        self._name_lower_to_idx: Dict[str, int] = {
            str(name).strip().lower(): idx for idx, name in enumerate(self.df["name"])
        }
        self._eng_name_lower_to_idx: Dict[str, int] = {
            str(eng).strip().lower(): idx
            for idx, eng in enumerate(self.df["english_name"])
            if pd.notna(eng) and str(eng).strip().lower() != "unknown"
        }

        # List of all titles for fuzzy matching fallback
        self._all_lookup_titles = list(self._name_lower_to_idx.keys()) + list(self._eng_name_lower_to_idx.keys())

    def find_anime_index(self, query: Union[str, int]) -> Tuple[int, pd.Series]:
        """
        Resolves an anime title or MAL ID to its dataframe index and row.
        
        Supports:
        1. Exact MAL ID match
        2. Exact case-insensitive name / English name match
        3. Substring match
        4. Levenshtein-based fuzzy match
        
        Raises:
            ValueError: If no reasonable match is found, with suggested titles if available.
        """
        # Case 1: Query is integer or string of digits (MAL ID)
        if isinstance(query, int) or (isinstance(query, str) and query.strip().isdigit()):
            mal_id = int(query)
            if mal_id in self._mal_id_to_idx:
                idx = self._mal_id_to_idx[mal_id]
                return idx, self.df.iloc[idx]
            raise ValueError(f"MAL ID {mal_id} not found in anime catalog.")

        # Case 2: Exact string match (case-insensitive)
        clean_q = str(query).strip().lower()
        if clean_q in self._name_lower_to_idx:
            idx = self._name_lower_to_idx[clean_q]
            return idx, self.df.iloc[idx]

        if clean_q in self._eng_name_lower_to_idx:
            idx = self._eng_name_lower_to_idx[clean_q]
            return idx, self.df.iloc[idx]

        # Case 3: Substring match (prioritize matches that start with query)
        for title, idx in self._name_lower_to_idx.items():
            if title.startswith(clean_q):
                return idx, self.df.iloc[idx]
        for title, idx in self._eng_name_lower_to_idx.items():
            if title.startswith(clean_q):
                return idx, self.df.iloc[idx]

        for title, idx in self._name_lower_to_idx.items():
            if clean_q in title:
                return idx, self.df.iloc[idx]

        # Case 4: Fuzzy matching fallback
        close_matches = difflib.get_close_matches(clean_q, self._all_lookup_titles, n=3, cutoff=0.6)
        if close_matches:
            best_match = close_matches[0]
            idx = self._name_lower_to_idx.get(best_match, self._eng_name_lower_to_idx.get(best_match))
            if idx is not None:
                matched_row = self.df.iloc[idx]
                logger.info(f"Fuzzy matched '{query}' -> '{matched_row['name']}' (ID: {matched_row['mal_id']})")
                return idx, matched_row

            suggestions_str = ", ".join(f"'{m}'" for m in close_matches)
            raise ValueError(f"Anime '{query}' not found. Did you mean: {suggestions_str}?")

        raise ValueError(f"Anime '{query}' not found in catalog and no close matches were identified.")

    def get_similarity_vector(self, query: Union[str, int]) -> np.ndarray:
        """
        Calculates cosine similarity vector for the query anime against all anime.
        
        Returns:
            1D numpy array of cosine similarity scores of length len(self.df).
        """
        idx, _ = self.find_anime_index(query)
        query_vec = self.tfidf_matrix[idx]
        sims = self.tfidf_matrix.dot(query_vec.T).toarray().ravel()
        return sims

    def recommend(
        self,
        query: Union[str, int],
        top_n: int = 10,
        exclude_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates Top-N content-based recommendations for an anime.
        
        Args:
            query: Title (string) or MAL ID (int) of the query anime.
            top_n: Number of recommendations to return (default: 10).
            exclude_ids: Optional list of MAL IDs to exclude from results.
            
        Returns:
            List of dictionaries containing recommended anime metadata.
        """
        if top_n <= 0:
            return []

        idx, query_row = self.find_anime_index(query)
        sims = self.get_similarity_vector(query)

        # Strictly exclude the input anime itself
        sims[idx] = -1.0

        # Exclude explicitly requested IDs
        if exclude_ids:
            for ex_id in exclude_ids:
                if ex_id in self._mal_id_to_idx:
                    sims[self._mal_id_to_idx[ex_id]] = -1.0

        # Get top-N indices sorted by similarity descending
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
                "similarity_score": round(sim_score, 4),
                "img_url": str(row.get("img_url", "")),
            }
            recommendations.append(rec_item)

        return recommendations
