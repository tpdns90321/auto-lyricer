from .repository import VideoRepository
from .dto import Video, RetrievalVideo, PaginatedResponse
from .exception import NotFoundException, NotFoundThings
from ..shared.supported import Platform as SupportedPlatform
from ..shared.exception import UnsupportedPlatformException
from urllib.parse import urlparse


class VideoService:
    def __init__(self, repository: VideoRepository):
        self._repository = repository

    async def retrieval_video(self, dto: RetrievalVideo) -> Video:
        platform, video_id = self._parse_video_url(dto.video_url)

        # Check if video already exists in database
        existing_video = await self._repository.get_video_by_video_id(
            platform, video_id
        )
        if existing_video:
            return existing_video

        # Retrieve new video from external source
        return await self._repository.retrieve_and_save_video(platform, video_id)

    def _parse_video_url(self, url: str) -> tuple[SupportedPlatform, str]:
        parsed_url = urlparse(url)

        if parsed_url.netloc in ["www.youtube.com", "youtube.com", "youtu.be"]:
            platform = SupportedPlatform.youtube
            video_id: str | None = None

            if parsed_url.netloc == "youtu.be":
                video_id = parsed_url.path[1:]
            else:
                queries = {
                    key: value
                    for query in parsed_url.query.split("&")
                    if (split := query.split("=")) and len(split) == 2
                    for key, value in [split]
                }
                video_id = queries.get("v")

            if not video_id:
                raise NotFoundException(NotFoundThings.video_id)

            return platform, video_id
        else:
            raise UnsupportedPlatformException(parsed_url.netloc)

    async def get_video_by_instance_id(self, instance_id: int) -> Video | None:
        return await self._repository.get_video_by_instance_id(instance_id)

    async def get_video_by_video_id(
        self, platform: SupportedPlatform, video_id: str
    ) -> Video | None:
        return await self._repository.get_video_by_video_id(platform, video_id)

    async def get_paginated_videos(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[Video]:
        """Get a paginated list of videos.

        Args:
            page: The page number, starting from 1.
            size: The number of items per page.

        Returns:
            A PaginatedResponse object containing the videos.
        """
        return await self._repository.get_paginated_videos(page, size)
