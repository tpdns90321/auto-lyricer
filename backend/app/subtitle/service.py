from .dto import CreateSubtitle, Subtitle
from .repository import SubtitleRepository
from ..shared.pagination import PaginatedResponse


class SubtitleService:
    def __init__(self, repository: SubtitleRepository):
        """Initialize SubtitleService with repository dependency.

        Args:
            repository: SubtitleRepository instance for data access.
        """
        self._repository = repository

    async def create_subtitle(self, dto: CreateSubtitle) -> Subtitle:
        return await self._repository.create_subtitle(dto)

    async def get_subtitle_by_instance_id(self, instance_id: int) -> Subtitle | None:
        return await self._repository.get_subtitle_by_instance_id(instance_id)

    async def get_paginated_subtitles(
        self, page: int = 1, size: int = 10, video_instance_id: int | None = None
    ) -> PaginatedResponse[Subtitle]:
        return await self._repository.get_paginated_subtitles(
            page, size, video_instance_id
        )
