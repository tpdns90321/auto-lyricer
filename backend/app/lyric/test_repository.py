from .repository import LyricRepository
from .dto import AddLyric
from ..database import AIOSqlite
from ..video.repository import VideoRepository
from ..video_retrieval.retrieval import VideoRetrieval
from ..video_retrieval.type import VideoInfo

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock


@pytest_asyncio.fixture
async def database() -> AIOSqlite:
    database = AIOSqlite(relative_path=":memory:")
    await database.reset_database()
    return database


@pytest_asyncio.fixture
async def normal_video_retrieval() -> VideoRetrieval:
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


@pytest_asyncio.fixture
async def lyric_repository(
    database: AIOSqlite, normal_video_retrieval
) -> LyricRepository:
    await VideoRepository(
        database=database,
        retrieval=normal_video_retrieval,
    ).retrieval_video("https://www.youtube.com/watch?v=testestest")
    return LyricRepository(database=database)


@pytest.mark.asyncio
async def test_lyric_repository_create_lyric(lyric_repository: LyricRepository):
    lyric = await lyric_repository.add_lyric(
        AddLyric(
            language="English",
            content="Hello, world!",
            video_instance_id=1,
        )
    )
    assert lyric.instance_id == 1


@pytest.mark.asyncio
async def test_lyric_repository_create_lyric_with_invalid_video(
    lyric_repository: LyricRepository,
):
    with pytest.raises(Exception):
        await lyric_repository.add_lyric(
            AddLyric(
                language="English",
                content="Hello, Bad World!",
                video_instance_id=9999,
            )
        )
