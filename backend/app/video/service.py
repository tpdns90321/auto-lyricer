from .repository import VideoRepository
from .dto import Video, RetrievalVideo
from ..shared.supported import Platform as SupportedPlatform


class VideoService:
    def __init__(self, repository: VideoRepository):
        self._repository = repository

    async def retrieval_video(self, dto: RetrievalVideo) -> Video:
        return await self._repository.retrieval_video(dto.video_url)

    async def get_video_by_instance_id(self, instance_id: int) -> Video | None:
        return await self._repository.get_video_by_instance_id(instance_id)

    async def get_video_by_video_id(
        self, platform: SupportedPlatform, video_id: str
    ) -> Video | None:
        return await self._repository.get_video_by_video_id(platform, video_id)
