from .service import VideoService
from .repository import VideoRepository
from .dto import Video, RetrievalVideo
from ..shared.supported import Platform as SupportedPlatform
from ..database import AIOSqlite
from ..video_retrieval import VideoRetrieval, VideoInfo

import pytest
import pytest_asyncio
from unittest import mock


@pytest.fixture
def normal_video_retrieval() -> VideoRetrieval:
    retrieval = VideoRetrieval({})
    retrieval.retrieval_video_info = mock.AsyncMock(
        return_value=VideoInfo(
            video_id="video_id",
            domain="youtube.com",
            duration_seconds=10,
            channel_name="channel_name",
            channel_id="channel_id",
            title="title",
            thumbnail_url="thumbnail_url",
        )
    )
    return retrieval


@pytest_asyncio.fixture
async def normal_video_service(normal_video_retrieval: VideoRetrieval) -> VideoService:
    database = AIOSqlite(":memory:")
    await database.reset_database()
    repository = VideoRepository(database, normal_video_retrieval)
    service = VideoService(repository)
    return service


@pytest_asyncio.fixture
async def failed_video_service(failed_video_retrieval: VideoRetrieval) -> VideoService:
    database = AIOSqlite(":memory:")
    await database.reset_database()
    repository = VideoRepository(database, failed_video_retrieval)
    service = VideoService(repository)
    return service


@pytest_asyncio.fixture
async def normal_video(normal_video_service: VideoService) -> Video:
    return await normal_video_service.retrieval_video(
        RetrievalVideo("https://www.youtube.com/watch?v=video_id")
    )


@pytest.mark.asyncio
async def test_retrieval_video(normal_video: Video):
    assert normal_video.video_id == "video_id"
    assert normal_video.platform == SupportedPlatform.youtube
    assert normal_video.duration_seconds == 10
    assert normal_video.channel_name == "channel_name"
    assert normal_video.channel_id == "channel_id"
    assert normal_video.title == "title"
    assert normal_video.thumbnail_url == "thumbnail_url"


@pytest.mark.asyncio
async def test_get_video_by_instance_id(
    normal_video_service: VideoService, normal_video: Video
):
    video = await normal_video_service.get_video_by_instance_id(
        normal_video.instance_id
    )
    assert video == normal_video


@pytest.mark.asyncio
async def test_get_video_by_instance_id_not_found(normal_video_service: VideoService):
    video = await normal_video_service.get_video_by_instance_id(0)
    assert video is None


@pytest.mark.asyncio
async def test_get_video_by_video_id(
    normal_video_service: VideoService, normal_video: Video
):
    video = await normal_video_service.get_video_by_video_id(
        SupportedPlatform.youtube, normal_video.video_id
    )
    assert video == normal_video


@pytest.mark.asyncio
async def test_get_video_by_video_id_not_found(normal_video_service: VideoService):
    video = await normal_video_service.get_video_by_video_id(
        SupportedPlatform.youtube, "not_found"
    )
    assert video is None
