
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class PaginatedResponse(Generic[T]):
    """A paginated response with metadata."""
    items: list[T] = field(
        metadata={"description": "List of items on the page.", "example": []}
    )
    total: int = field(
        metadata={"description": "Total number of items in full result set.", "example": 123}
    )
    page: int = field(
        metadata={"description": "Current page number (1-based).", "example": 2}
    )
    size: int = field(
        metadata={"description": "Number of items per page.", "example": 20}
    )
