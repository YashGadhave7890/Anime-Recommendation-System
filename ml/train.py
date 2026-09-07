"""
Model Training and Artifact Persistence Pipeline.
Fits TF-IDF vectorizer, computes sparse feature matrix, and serializes
all required recommendation artifacts to ml/models/.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.config import (
    ANIME_INDEX_PATH,
    MODEL_METADATA_PATH,
    MODELS_DIR,
    PROCESSED_PARQUET_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
    TFIDF_VECTORIZER_PATH,
)
from ml.feature_engineering import build_and_save_pipeline
from ml.utils import save_json, setup_logger

logger = setup_logger("ModelTrainer")


def train_and_persist_models(force_data_rebuild: bool = False) -> Dict[str, Any]:
    """
    Fits TF-IDF representations on the cleaned anime dataset and serializes
    models, matrices, and indexing lookup tables to ml/models/.
    
    Returns:
        Summary dictionary of model metadata and training parameters.
    """
    logger.info("Starting ANIMORA recommendation model training...")
    start_time = time.time()

    # 1. Ensure processed dataset exists
    if not PROCESSED_PARQUET_PATH.exists() or force_data_rebuild:
        logger.info("Processed parquet not found or rebuild requested. Executing Phase 1 pipeline...")
        df, _ = build_and_save_pipeline()
    else:
        logger.info(f"Loading preprocessed dataset from {PROCESSED_PARQUET_PATH}...")
        df = pd.read_parquet(PROCESSED_PARQUET_PATH)

    logger.info(f"Loaded {len(df):,} anime records for vectorization.")

    # 2. Fit TF-IDF Vectorizer
    logger.info(
        f"Fitting TfidfVectorizer (max_features={TFIDF_MAX_FEATURES:,}, "
        f"ngram_range={TFIDF_NGRAM_RANGE}, sublinear_tf={TFIDF_SUBLINEAR_TF})..."
    )
    t_vec = time.time()
    vectorizer = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        ngram_range=TFIDF_NGRAM_RANGE,
        stop_words="english",
        sublinear_tf=TFIDF_SUBLINEAR_TF,
    )
    tfidf_matrix = vectorizer.fit_transform(df["content_soup"].fillna(""))
    vec_duration = time.time() - t_vec
    logger.info(
        f"Vectorization complete in {vec_duration:.2f}s: Matrix shape={tfidf_matrix.shape}, "
        f"Non-zeros={tfidf_matrix.nnz:,} ({tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]) * 100:.2f}% density)"
    )

    # 3. Create Lightweight Anime Index DataFrame
    index_cols = [
        "mal_id",
        "name",
        "english_name",
        "japanese_name",
        "score",
        "weighted_score",
        "genres",
        "type",
        "episodes",
        "members",
        "log_members",
        "release_year",
        "img_url",
    ]
    avail_cols = [c for c in index_cols if c in df.columns]
    anime_index_df = df[avail_cols].copy()

    # 4. Serialize Artifacts to ml/models/
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving vectorizer to {TFIDF_VECTORIZER_PATH}...")
    joblib.dump(vectorizer, TFIDF_VECTORIZER_PATH, compress=3)

    logger.info(f"Saving sparse TF-IDF matrix to {TFIDF_MATRIX_PATH}...")
    save_npz(TFIDF_MATRIX_PATH, tfidf_matrix)

    logger.info(f"Saving indexed lookup dataframe to {ANIME_INDEX_PATH}...")
    anime_index_df.to_parquet(ANIME_INDEX_PATH, index=False)

    # 5. Metadata and Diagnostics
    total_duration = time.time() - start_time
    metadata = {
        "model_version": "2.0.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "total_records": len(df),
        "vocab_size": len(vectorizer.vocabulary_),
        "matrix_shape": list(tfidf_matrix.shape),
        "matrix_non_zeros": int(tfidf_matrix.nnz),
        "training_time_seconds": round(total_duration, 2),
        "vectorizer_params": {
            "max_features": TFIDF_MAX_FEATURES,
            "ngram_range": list(TFIDF_NGRAM_RANGE),
            "sublinear_tf": TFIDF_SUBLINEAR_TF,
        },
        "artifact_paths": {
            "vectorizer": str(TFIDF_VECTORIZER_PATH.name),
            "matrix": str(TFIDF_MATRIX_PATH.name),
            "index": str(ANIME_INDEX_PATH.name),
        },
    }

    save_json(metadata, MODEL_METADATA_PATH)
    logger.info(f"Saved model metadata to {MODEL_METADATA_PATH}.")
    logger.info(f"ANIMORA Model Training completed successfully in {total_duration:.2f}s!")

    return metadata


if __name__ == "__main__":
    meta = train_and_persist_models()
    print("\n--- Model Training Summary ---")
    print(f"Total Records Vectorized: {meta['total_records']:,}")
    print(f"Vocabulary Size: {meta['vocab_size']:,}")
    print(f"Matrix Non-Zeros: {meta['matrix_non_zeros']:,}")
    print(f"Duration: {meta['training_time_seconds']}s")
    print(f"Artifacts saved in: {MODELS_DIR}")
