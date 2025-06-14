from app.video_retrieval.type import VideoInfo
from .model import Video as VideoModel
from .dto import Video as VideoDTO
from .exception import (
    NotFoundError,
    NotFoundThings,
)
from ..shared.supported import Platform as SupportedPlatform
from ..shared.pagination import PaginatedResponse
from ..shared.exception import (
    UnknownError,
)
from ..database.async_sqlalchemy import AsyncSQLAlchemy

from yt_dlp import DownloadError
from sqlalchemy.sql import Select, and_
from sqlalchemy.sql.functions import count


class VideoRepository:
    def __init__(self, database: AsyncSQLAlchemy):
        """Initialize VideoRepository with database and video retrieval service.

        Args:
            database: AsyncSQLAlchemy database instance.
            retrieval: VideoRetrieval service for fetching video information.
        """
        self._session_factory = database.session

    async def retrieve_and_save_video(
        self, platform: SupportedPlatform, video_id: str, video: VideoInfo
    ) -> VideoDTO:
        try:
            # Save video to database
            async with self._session_factory() as session:
                model = VideoModel(
                    platform=platform,
                    video_id=video_id,
                    channel_id=video.channel_id,
                    channel_name=video.channel_name,
                    title=video.title,
                    description=video.description,
                    duration_seconds=video.duration_seconds,
                    thumbnail_url=video.thumbnail_url,
                )
                session.add(model)
                await session.commit()
                return _model_to_dto(model)
        except DownloadError as e:
            raise NotFoundError(NotFoundThings.video) from e
        except Exception as e:
            raise UnknownError(e) from e

    async def get_video_by_instance_id(self, instance_id: int) -> VideoDTO | None:
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    Select(VideoModel).filter(VideoModel.instance_id == instance_id)
                )
                model = result.scalar_one_or_none()
                return _model_to_dto(model) if model else None
        except Exception as e:
            raise UnknownError(e) from e

    async def get_video_by_video_id(
        self, platform: SupportedPlatform, video_id: str
    ) -> VideoDTO | None:
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    Select(VideoModel).filter(
                        and_(
                            VideoModel.video_id == video_id,
                            VideoModel.platform == platform.value,
                        )
                    )
                )
                model = result.scalar_one_or_none()
                return _model_to_dto(model) if model else None
        except Exception as e:
            raise UnknownError(e) from e

    async def get_paginated_videos(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[VideoDTO]:
        """Get a paginated list of videos.

        Args:
            page: The page number, starting from 1.
            size: The number of items per page.

        Returns:
            A PaginatedResponse object containing the videos.
        """
        try:
            async with self._session_factory() as session:
                # Calculate offset based on page and size
                offset = (page - 1) * size

                # Get total count
                total_query = Select(count(VideoModel.instance_id))
                total_result = await session.execute(total_query)
                total = total_result.scalar()
                if total is None:
                    total = 0

                # Get paginated results
                query = Select(VideoModel).limit(size).offset(offset)
                result = await session.execute(query)

                items = [_model_to_dto(model) for model in result.scalars()]

                return PaginatedResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            raise UnknownError(e) from e


def _model_to_dto(model: VideoModel) -> VideoDTO:
    return VideoDTO(**model.to_dict())
