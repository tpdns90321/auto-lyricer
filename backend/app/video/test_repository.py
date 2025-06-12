from .repository import VideoRepository
from .dto import Video
from ..shared.supported import Platform as SupportedPlatform
from ..database import AIOSqlite
from ..video_retrieval import VideoInfo

import pytest
import pytest_asyncio


@pytest.fixture
def normal_video_info() -> VideoInfo:
    return VideoInfo(
        video_id="testestest",
        description="Hello world",
        domain="youtube.com",
        duration_seconds=100,
        channel_name="channel",
        channel_id="channel_id",
        title="",
        thumbnail_url="thumbnail_url",
    )


@pytest_asyncio.fixture
async def database() -> AIOSqlite:
    database = AIOSqlite(relative_path=":memory:")
    await database.reset_database()
    return database


@pytest_asyncio.fixture
async def normal_repository(database) -> VideoRepository:
    return VideoRepository(database=database)


@pytest_asyncio.fixture
async def normal_video(normal_repository, normal_video_info: VideoInfo) -> Video:
    return await normal_repository.retrieve_and_save_video(
        platform=SupportedPlatform.youtube,
        video_id="testestest",
        video=normal_video_info,
    )


@pytest.mark.asyncio
async def test_retrieve_and_save_video_normal(normal_video: Video):
    assert normal_video.instance_id == 1
    assert normal_video.video_id == "testestest"
    assert normal_video.platform == SupportedPlatform.youtube
    assert normal_video.channel_id == "channel_id"
    assert normal_video.channel_name == "channel"
    assert normal_video.description == "Hello world"
    assert normal_video.duration_seconds == 100
    assert normal_video.thumbnail_url == "thumbnail_url"


@pytest.mark.asyncio
async def test_retrieve_and_save_video_duplicate(
    normal_repository: VideoRepository, normal_video: Video
):
    # Test that trying to retrieve the same video returns the existing one
    # This is now handled by the service layer, so we test get_video_by_video_id
    second_try = await normal_repository.get_video_by_video_id(
        platform=SupportedPlatform.youtube, video_id="testestest"
    )
    assert normal_video.instance_id == 1
    assert second_try is not None
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


@pytest.mark.asyncio
async def test_get_paginated_videos(
    normal_repository: VideoRepository, normal_video_info: VideoInfo
):
    # Create multiple videos for pagination testing
    for i in range(15):  # Adding 15 videos
        # Mock a different video ID each time
        video_info = VideoInfo(
            video_id=f"test{i}",
            domain="youtube.com",
            duration_seconds=100,
            channel_name="channel",
            channel_id="channel_id",
            title=f"Test Video {i}",
            thumbnail_url="thumbnail_url",
        )
        await normal_repository.retrieve_and_save_video(
            platform=SupportedPlatform.youtube,
            video_id=f"test{i}",
            video=video_info,
        )

    # Test first page with default values (page=1, size=10)
    paginated = await normal_repository.get_paginated_videos()
    assert paginated.page == 1
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 10

    # Test second page
    paginated = await normal_repository.get_paginated_videos(page=2)
    assert paginated.page == 2
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 5

    # Test with custom page size
    paginated = await normal_repository.get_paginated_videos(page=1, size=5)
    assert paginated.page == 1
    assert paginated.size == 5
    assert paginated.total == 15
    assert len(paginated.items) == 5

    # Test page beyond available data
    paginated = await normal_repository.get_paginated_videos(page=4)
    assert paginated.page == 4
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 0
