from .dto import AddLyric, Lyric, PaginatedResponse
from .repository import LyricRepository


class LyricService:
    def __init__(self, lyric_repository: LyricRepository):
        self._lyric_repository = lyric_repository

    async def add_lyric(self, dto: AddLyric) -> Lyric:
        return await self._lyric_repository.add_lyric(dto)

    async def get_lyric_by_instance_id(self, instance_id: int) -> Lyric | None:
        return await self._lyric_repository.get_lyric_by_instance_id(instance_id)

    async def get_list_of_lyrics_by_video_instance_id(
        self, video_instance_id: int
    ) -> list[Lyric]:
        return await self._lyric_repository.get_list_of_lyrics_by_video_instance_id(
            video_instance_id
        )

    async def get_paginated_lyrics(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[Lyric]:
        return await self._lyric_repository.get_paginated_lyrics(page, size)
