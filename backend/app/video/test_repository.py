from .repository import VideoRepository
from .dto import SupportedPlatform, Video
from ..database import AIOSqlite
from ..video_retrieval import VideoInfo
from ..video.exception import (
    NotFoundException,
    UnsupportedPlatformException,
)
from ..video_retrieval import VideoRetrieval

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from yt_dlp import DownloadError


@pytest.fixture
def normal_video_retrieval() -> VideoRetrieval:
    retrieval = VideoRetrieval({})
    retrieval.retrieval_video_info = AsyncMock(
        return_value=VideoInfo(
            video_id="testestest",
            domain="youtube.com",
            duration_seconds=100,
            channel_name="channel",
            channel_id="channel_id",
            title="",
            thumbnail_url="thumbnail_url",
        )
    )
    return retrieval


@pytest.fixture
def failed_video_retrieval() -> VideoRetrieval:
    retrieval = VideoRetrieval({})
    retrieval.retrieval_video_info = AsyncMock(
        side_effect=DownloadError("Failed to retrieve video info")
    )
    return retrieval


@pytest_asyncio.fixture
async def database() -> AIOSqlite:
    database = AIOSqlite(relative_path=":memory:")
    await database.reset_database()
    return database


@pytest_asyncio.fixture
async def normal_repository(database, normal_video_retrieval) -> VideoRepository:
    return VideoRepository(database=database, retrieval=normal_video_retrieval)


@pytest_asyncio.fixture
async def failed_repository(database, failed_video_retrieval) -> VideoRepository:
    return VideoRepository(database=database, retrieval=failed_video_retrieval)


@pytest_asyncio.fixture
async def normal_video(normal_repository) -> Video:
    return await normal_repository.retrieval_video(
        url="https://www.youtube.com/watch?v=testestest&si=123"
    )


@pytest.mark.asyncio
async def test_retrieval_video_normal(normal_video: Video):
    assert normal_video.instance_id == 1
    assert normal_video.video_id == "testestest"
    assert normal_video.platform == SupportedPlatform.youtube
    assert normal_video.channel_id == "channel_id"
    assert normal_video.channel_name == "channel"
    assert normal_video.duration_seconds == 100
    assert normal_video.thumbnail_url == "thumbnail_url"


@pytest.mark.asyncio
async def test_retrieval_video_not_found(failed_repository: VideoRepository):
    with pytest.raises(NotFoundException):
        await failed_repository.retrieval_video(
            url="https://www.youtube.com/watch?v=aaaaaaaaaaa&si=123"
        )


@pytest.mark.asyncio
async def test_retrieval_video_unsupported_platform(normal_repository: VideoRepository):
    with pytest.raises(UnsupportedPlatformException):
        await normal_repository.retrieval_video(url="https://www.naver.com")


@pytest.mark.asyncio
async def test_retrieval_video_duplicate(
    normal_repository: VideoRepository, normal_video: Video
):
    async def retrieval_video() -> Video:
        return await normal_repository.retrieval_video(
            url="https://youtu.be/testestest?si=123"
        )

    second_try = await retrieval_video()
    assert normal_video.instance_id == 1
    assert normal_video.instance_id == second_try.instance_id
    assert normal_video.video_id == second_try.video_id


@pytest.mark.asyncio
async def test_get_video_by_instance_id_normal(
    normal_repository: VideoRepository, normal_video: Video
):
    result = await normal_repository.get_video_by_instance_id(
        instance_id=normal_video.instance_id
    )

    assert result is not None
    assert result.video_id == normal_video.video_id
    assert result.platform == normal_video.platform


@pytest.mark.asyncio
async def test_get_video_by_instance_id_not_found(normal_repository: VideoRepository):
    result = await normal_repository.get_video_by_instance_id(instance_id=999999)

    assert result is None


@pytest.mark.asyncio
async def test_get_video_by_video_id_normal(
    normal_repository: VideoRepository, normal_video: Video
):
    result: Video | None = await normal_repository.get_video_by_video_id(
        platform=normal_video.platform, video_id=normal_video.video_id
    )

    assert result is not None
    assert result.video_id == normal_video.video_id
    assert result.platform == normal_video.platform


@pytest.mark.asyncio
async def test_get_video_by_video_id_not_found(normal_repository: VideoRepository):
    result = await normal_repository.get_video_by_video_id(
        platform=SupportedPlatform["youtube"], video_id="aaaaaaaaaaa"
    )

    assert result is None
