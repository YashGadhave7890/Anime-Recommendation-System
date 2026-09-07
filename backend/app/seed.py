"""
Database Seeding Script for ANIMORA.
Populates anime catalog references from the processed Parquet dataset
and creates demo users with initial interactions for local evaluation.
"""

import time
from typing import Dict
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.config import PROCESSED_PARQUET_PATH, settings
from backend.app.database import SessionLocal, init_db
from backend.app.models.anime import AnimeReference
from backend.app.models.interactions import (
    Rating,
    UserPreference,
    WatchHistory,
    WatchlistItem,
)
from backend.app.models.user import User
from ml.utils import setup_logger

logger = setup_logger("DBSeeder")


def seed_database(force: bool = False) -> Dict[str, int]:
    """
    Seeds the SQLite database from cleaned_anime.parquet.
    
    Args:
        force: If True, clears existing tables and re-seeds from scratch.
        
    Returns:
        Summary counts dictionary.
    """
    init_db()
    db: Session = SessionLocal()

    try:
        anime_count = db.query(AnimeReference).count()
        if anime_count > 0 and not force:
            logger.info(f"Database already seeded with {anime_count:,} anime records. Skipping catalog re-seed.")
        else:
            if force:
                logger.info("Force re-seed requested. Clearing existing records...")
                db.query(Rating).delete()
                db.query(WatchlistItem).delete()
                db.query(WatchHistory).delete()
                db.query(UserPreference).delete()
                db.query(AnimeReference).delete()
                db.query(User).delete()
                db.commit()

            logger.info(f"Loading anime catalog from {PROCESSED_PARQUET_PATH}...")
            t0 = time.time()
            df = pd.read_parquet(PROCESSED_PARQUET_PATH)

            # Map DataFrame columns to AnimeReference fields
            records = []
            for _, row in df.iterrows():
                rec = {
                    "mal_id": int(row["mal_id"]),
                    "name": str(row["name"]),
                    "english_name": str(row["english_name"]) if pd.notna(row.get("english_name")) and str(row["english_name"]).lower() != "unknown" else None,
                    "japanese_name": str(row["japanese_name"]) if pd.notna(row.get("japanese_name")) and str(row["japanese_name"]).lower() != "unknown" else None,
                    "score": float(row["score"]) if pd.notna(row.get("score")) else None,
                    "weighted_score": float(row["weighted_score"]) if pd.notna(row.get("weighted_score")) else 0.0,
                    "genres": str(row.get("genres", "")),
                    "type": str(row.get("type", "Unknown")),
                    "episodes": float(row["episodes"]) if pd.notna(row.get("episodes")) else None,
                    "members": int(row["members"]) if pd.notna(row.get("members")) else 0,
                    "release_year": int(row["release_year"]) if pd.notna(row.get("release_year")) else None,
                    "synopsis": str(row.get("synopsis", "")),
                    "img_url": str(row.get("img_url", "")) if pd.notna(row.get("img_url")) else None,
                }
                records.append(rec)

            logger.info(f"Bulk inserting {len(records):,} anime records into SQLite database...")
            # Chunked bulk insert
            chunk_size = 5000
            for i in range(0, len(records), chunk_size):
                db.bulk_insert_mappings(AnimeReference, records[i:i + chunk_size])
                db.commit()

            logger.info(f"Seeded {len(records):,} anime records in {time.time() - t0:.2f}s.")

        # Seed Demo User 1: Active user with ratings, watchlist, and preferences
        demo_user = db.query(User).filter(User.id == settings.DEFAULT_USER_ID).first()
        if not demo_user:
            demo_user = User(
                id=settings.DEFAULT_USER_ID,
                username=settings.DEFAULT_USERNAME,
                display_name=settings.DEFAULT_DISPLAY_NAME,
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

        # Seed Demo Ratings
        demo_ratings = [
            {"anime_id": 1535, "rating": 10.0, "review": "Masterpiece psychological cat-and-mouse thriller."},  # Death Note
            {"anime_id": 5114, "rating": 9.5, "review": "Incredible worldbuilding and emotional depth."},       # FMA: Brotherhood
            {"anime_id": 9253, "rating": 9.0, "review": "Brilliant time travel narrative."},                   # Steins;Gate
            {"anime_id": 28891, "rating": 4.0, "review": "High school volleyball wasn't quite my thing."},     # Haikyuu!!
        ]
        for dr in demo_ratings:
            exists = db.query(Rating).filter(
                Rating.user_id == demo_user.id,
                Rating.anime_id == dr["anime_id"]
            ).first()
            if not exists and db.query(AnimeReference).filter(AnimeReference.mal_id == dr["anime_id"]).first():
                db.add(Rating(user_id=demo_user.id, **dr))
        db.commit()

        # Seed Demo Watchlist
        demo_watchlist = [
            {"anime_id": 1, "status": "plan_to_watch"},     # Cowboy Bebop
            {"anime_id": 1575, "status": "watching"},       # Code Geass
        ]
        for dw in demo_watchlist:
            exists = db.query(WatchlistItem).filter(
                WatchlistItem.user_id == demo_user.id,
                WatchlistItem.anime_id == dw["anime_id"]
            ).first()
            if not exists and db.query(AnimeReference).filter(AnimeReference.mal_id == dw["anime_id"]).first():
                db.add(WatchlistItem(user_id=demo_user.id, **dw))
        db.commit()

        # Seed Demo Preferences
        demo_pref = db.query(UserPreference).filter(UserPreference.user_id == demo_user.id).first()
        if not demo_pref:
            demo_pref = UserPreference(
                user_id=demo_user.id,
                preferred_genres="Psychological, Sci-Fi, Thriller",
                preferred_types="TV, Movie",
            )
            db.add(demo_pref)
            db.commit()

        # Seed Demo User 2: Cold-start user with 0 ratings and 0 preferences
        cold_user = db.query(User).filter(User.id == 2).first()
        if not cold_user:
            cold_user = User(
                id=2,
                username="new_user",
                display_name="New Otaku",
            )
            db.add(cold_user)
            db.commit()

        summary = {
            "anime_records": db.query(AnimeReference).count(),
            "users": db.query(User).count(),
            "ratings": db.query(Rating).count(),
            "watchlist_items": db.query(WatchlistItem).count(),
            "preferences": db.query(UserPreference).count(),
        }
        logger.info(f"Database seed complete: {summary}")
        return summary
    finally:
        db.close()


if __name__ == "__main__":
    res = seed_database()
    print("\n--- Database Seed Summary ---")
    for k, v in res.items():
        print(f"{k}: {v:,}")
