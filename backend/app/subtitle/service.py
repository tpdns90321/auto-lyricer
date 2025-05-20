from .dto import CreateSubtitle, Subtitle, PaginatedResponse
from .repository import SubtitleRepository


class SubtitleService:
    def __init__(self, repository: SubtitleRepository):
        self._repository = repository

    async def create_subtitle(self, dto: CreateSubtitle) -> Subtitle:
        return await self._repository.create_subtitle(dto)

    async def get_subtitle_by_instance_id(
        self, instance_id: int
    ) -> Subtitle | None:
        return await self._repository.get_subtitle_by_instance_id(instance_id)

    async def get_list_of_subtitles_by_video_instance_id(
        self, video_instance_id: int
    ) -> list[Subtitle]:
        return await self._repository.get_list_of_subtitles_by_video_instance_id(
            video_instance_id
        )

    async def get_paginated_subtitles(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[Subtitle]:
        return await self._repository.get_paginated_subtitles(page, size)