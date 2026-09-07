"""
Dependencies package exports.
"""

from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.db import get_db

__all__ = ["get_db", "get_current_user"]
