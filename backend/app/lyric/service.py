from .dto import AddLyric, Lyric
from .repository import LyricRepository
from ..shared.pagination import PaginatedResponse


class LyricService:
    def __init__(self, lyric_repository: LyricRepository):
        """Initialize LyricService with repository.

        Args:
            lyric_repository: LyricRepository instance for data access.
        """
        self._lyric_repository = lyric_repository

    async def add_lyric(self, dto: AddLyric) -> Lyric:
        return await self._lyric_repository.add_lyric(dto)

    async def get_lyric_by_instance_id(self, instance_id: int) -> Lyric | None:
        return await self._lyric_repository.get_lyric_by_instance_id(instance_id)

    async def get_paginated_lyrics(
        self, page: int = 1, size: int = 10, video_instance_id: int | None = None
    ) -> PaginatedResponse[Lyric]:
        return await self._lyric_repository.get_paginated_lyrics(
            page, size, video_instance_id
        )
