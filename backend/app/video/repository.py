from .model import Video as VideoModel
from .dto import Video as VideoDTO
from .exception import (
    NotFoundException,
    NotFoundThings,
)
from ..shared.supported import Platform as SupportedPlatform
from ..shared.exception import (
    UnknownException,
    UnsupportedPlatformException,
)
from ..database import AsyncSQLAlchemy
from ..video_retrieval import VideoRetrieval

from yt_dlp import DownloadError
from sqlalchemy.sql import Select, and_
from urllib.parse import urlparse


class VideoRepository:
    def __init__(self, database: AsyncSQLAlchemy, retrieval: VideoRetrieval):
        self._session_factory = database.session
        self._retrieval = retrieval

    async def retrieval_video(self, url: str) -> VideoDTO:
        parsed_url = urlparse(url)
        platform = parsed_url.netloc
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
                video_id = queries.get("v", None)

            if not video_id:
                raise NotFoundException(NotFoundThings.video_id)

            model = await self.get_video_by_video_id(
                platform=platform, video_id=video_id
            )

            if model:
                return model
        else:
            raise UnsupportedPlatformException(parsed_url.netloc)

        try:
            recreated_url = ""
            if platform == SupportedPlatform.youtube:
                recreated_url = f"https://www.youtube.com/watch?v={video_id}"

            video = await self._retrieval.retrieval_video_info(recreated_url)
            if not video:
                raise NotFoundException(NotFoundThings.video)

            async with self._session_factory() as session:
                model = VideoModel(
                    platform=platform,
                    video_id=video.video_id,
                    channel_id=video.channel_id,
                    channel_name=video.channel_name,
                    title=video.title,
                    duration_seconds=video.duration_seconds,
                    thumbnail_url=video.thumbnail_url,
                )
                session.add(model)
                await session.commit()
                return _model_to_dto(model)
        except DownloadError:
            raise NotFoundException(NotFoundThings.video)
        except Exception as e:
            raise UnknownException(e)

    async def get_video_by_instance_id(self, instance_id: int) -> VideoDTO | None:
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    Select(VideoModel).filter(VideoModel.instance_id == instance_id)
                )
                model = result.scalar_one_or_none()
                return _model_to_dto(model) if model else None
        except Exception as e:
            raise UnknownException(e)

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
            raise UnknownException(e)


def _model_to_dto(model: VideoModel) -> VideoDTO:
    return VideoDTO(**model.to_dict())
