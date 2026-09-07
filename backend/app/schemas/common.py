"""
Common generic schemas for pagination, health checks, and messages.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Healthcheck response status."""
    status: str
    version: str
    database: str
    ml_engine: str
    records_loaded: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list wrapper."""
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
