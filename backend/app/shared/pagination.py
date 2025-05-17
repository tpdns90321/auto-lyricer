from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
