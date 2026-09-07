"""
Utility functions for text processing, data normalization, logging, and serialization.
"""

import html
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def setup_logger(name: str = "ANIMORA", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


def clean_text(text: Optional[str]) -> str:
    """
    Cleans raw synopsis and text fields:
    - Decodes HTML entities (&quot;, &#039;, etc.)
    - Removes HTML tags
    - Removes MAL rewrite and source attribution notices
    - Normalizes whitespace, quotes, and punctuation
    """
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""

    text = str(text)

    # Decode HTML entities
    text = html.unescape(text)

    # Remove HTML tags (e.g. <br>, <i>, etc.)
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove MAL rewrite and source attributions
    text = re.sub(r"\[Written by MAL Rewrite\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(Source:.*?\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[Source:.*?\]", "", text, flags=re.IGNORECASE)

    # Remove non-standard unicode artifacts (e.g.  or odd control characters)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ufffd]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def parse_genres(genre_raw: Any) -> Tuple[List[str], str]:
    """
    Parses genre field from various formats (eval-string list "['Action', 'Adventure']",
    comma-separated string "Action, Adventure", or already a list) into a list and clean string.
    """
    if genre_raw is None or (isinstance(genre_raw, float) and np.isnan(genre_raw)):
        return [], ""

    if isinstance(genre_raw, list):
        genres = [str(g).strip() for g in genre_raw if str(g).strip() and str(g).lower() != "unknown"]
        return genres, ", ".join(genres)

    genre_str = str(genre_raw).strip()
    if not genre_str or genre_str.lower() in ["unknown", "none", "nan"]:
        return [], ""

    # Check if string starts with '[' and ends with ']'
    if genre_str.startswith("[") and genre_str.endswith("]"):
        # Strip brackets and split by comma, then strip quotes
        items = re.findall(r"['\"]([^'\"]+)['\"]", genre_str)
        if not items:
            items = [item.strip(" '\"[]") for item in genre_str.split(",") if item.strip(" '\"[]")]
    else:
        items = [item.strip() for item in genre_str.split(",") if item.strip()]

    # Filter out empty or "Unknown"
    cleaned = [g for g in items if g and g.lower() not in ["unknown", "none", "nan", ""]]
    return cleaned, ", ".join(cleaned)


def extract_release_info(premiered: Any, aired: Any) -> Tuple[Optional[int], str]:
    """
    Extracts release year (int) and release season ('Spring', 'Summer', 'Fall', 'Winter', or 'Unknown')
    from premiered (e.g., 'Spring 2016') or aired (e.g., 'Oct 4, 2015 to Mar 27, 2016').
    """
    seasons = ["Spring", "Summer", "Fall", "Winter"]
    found_year: Optional[int] = None
    found_season: str = "Unknown"

    # Try premiered first (e.g. "Spring 2016")
    if premiered is not None and not (isinstance(premiered, float) and np.isnan(premiered)):
        p_str = str(premiered).strip()
        if p_str.lower() not in ["unknown", "nan", "none"]:
            # Check season
            for s in seasons:
                if re.search(rf"\b{s}\b", p_str, re.IGNORECASE):
                    found_season = s
                    break
            # Check 4-digit year
            year_match = re.search(r"\b(19\d\d|20\d\d)\b", p_str)
            if year_match:
                found_year = int(year_match.group(1))

    # If year not found, extract from aired string (e.g. "Oct 4, 2015 to Mar 27, 2016")
    if found_year is None and aired is not None and not (isinstance(aired, float) and np.isnan(aired)):
        a_str = str(aired).strip()
        if a_str.lower() not in ["unknown", "nan", "none"]:
            year_match = re.search(r"\b(19\d\d|20\d\d)\b", a_str)
            if year_match:
                found_year = int(year_match.group(1))

    return found_year, found_season


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Serializes data to a JSON file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Loads and deserializes JSON from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
