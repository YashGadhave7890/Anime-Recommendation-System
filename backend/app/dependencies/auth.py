"""
Lightweight authentication and demo user resolution dependency.
Provides zero-friction local user tracking without passwords or complex tokens.
"""

from typing import Optional
from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User


def get_current_user(
    x_user_id: Optional[int] = Header(None, alias="X-User-Id", description="User ID override header."),
    user_id: Optional[int] = Query(None, description="User ID override query parameter."),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves the current requesting user:
    1. Checks X-User-Id request header
    2. Checks user_id query parameter
    3. Defaults to the local demo user (ID: 1, 'demo_user')
    Creates the default demo user automatically if it does not yet exist.
    """
    target_id = x_user_id if x_user_id is not None else user_id

    if target_id is not None:
        user = db.query(User).filter(User.id == target_id).first()
        if not user:
            # Auto-create if testing with a new user ID like 2
            user = User(
                id=target_id,
                username=f"user_{target_id}",
                display_name=f"Demo User {target_id}",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # Default demo user
    user = db.query(User).filter(User.id == settings.DEFAULT_USER_ID).first()
    if not user:
        user = User(
            id=settings.DEFAULT_USER_ID,
            username=settings.DEFAULT_USERNAME,
            display_name=settings.DEFAULT_DISPLAY_NAME,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
