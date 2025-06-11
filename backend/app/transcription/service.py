from .dto import CreateTranscription, Transcription
from .repository import TranscriptionRepository
from ..shared.pagination import PaginatedResponse


class TranscriptionService:
    def __init__(self, repository: TranscriptionRepository):
        """Initialize TranscriptionService with repository dependency.

        Args:
            repository: TranscriptionRepository instance for data access.
        """
        self._repository = repository

    async def create_transcription(self, dto: CreateTranscription) -> Transcription:
        return await self._repository.create_transcription(dto)

    async def get_transcription_by_instance_id(
        self, instance_id: int
    ) -> Transcription | None:
        return await self._repository.get_transcription_by_instance_id(instance_id)

    async def get_paginated_transcriptions(
        self, page: int = 1, size: int = 10, video_instance_id: int | None = None
    ) -> PaginatedResponse[Transcription]:
        return await self._repository.get_paginated_transcriptions(
            page, size, video_instance_id
        )
