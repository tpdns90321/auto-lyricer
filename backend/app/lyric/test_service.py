from ..database import AIOSqlite
from ..shared.supported import Language
from ..video_retrieval import VideoRetrieval, VideoInfo
from ..video.repository import VideoRepository
from .repository import LyricRepository
from .service import LyricService
from .dto import AddLyric, Lyric
from .exception import NotFoundThing, NotFoundThingException

import pytest_asyncio
import pytest
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


@pytest_asyncio.fixture
async def lyric_service(lyric_repository: LyricRepository) -> LyricService:
    return LyricService(lyric_repository)


@pytest_asyncio.fixture
async def normal_lyric(lyric_service: LyricService) -> Lyric:
    return await lyric_service.add_lyric(
        AddLyric(
            language=Language.english,
            content="Hello, world!",
            video_instance_id=1,
        )
    )


@pytest.mark.asyncio
async def test_lyric_service_add_lyric(normal_lyric: Lyric):
    assert normal_lyric.instance_id == 1
    assert normal_lyric.language == Language.english
    assert normal_lyric.content == "Hello, world!"
    assert normal_lyric.video_instance_id == 1


@pytest.mark.asyncio
async def test_lyric_service_add_lyric_with_invalid_video(
    lyric_service: LyricService,
):
    dto = AddLyric(
        language=Language.english,
        content="Hello, Bad World!",
        video_instance_id=9999,
    )
    with pytest.raises(NotFoundThingException) as notFoundException:
        await lyric_service.add_lyric(dto)
    assert notFoundException.value.thing == NotFoundThing.VideoInstance


@pytest.mark.asyncio
async def test_lyric_service_get_lyric_by_instance_id(
    lyric_service: LyricService, normal_lyric: Lyric
):
    lyric = await lyric_service.get_lyric_by_instance_id(1)
    assert lyric is not None
    assert lyric.language == normal_lyric.language
    assert lyric.content == normal_lyric.content
    assert lyric.video_instance_id == normal_lyric.video_instance_id


@pytest.mark.asyncio
async def test_lyric_service_get_lyric_by_instance_id_not_found(
    lyric_service: LyricService,
):
    lyric = await lyric_service.get_lyric_by_instance_id(9999)
    assert lyric is None


@pytest.mark.asyncio
async def test_lyric_service_get_paginated_lyrics_by_video_instance_id(
    lyric_service: LyricService, normal_lyric: Lyric
):
    result = await lyric_service.get_paginated_lyrics(page=1, size=10, video_instance_id=1)
    assert len(result.items) == 1
    assert result.total == 1
    assert result.items[0].instance_id == normal_lyric.instance_id
    assert result.items[0].language == normal_lyric.language
    assert result.items[0].content == normal_lyric.content


@pytest.mark.asyncio
async def test_lyric_service_get_paginated_lyrics_by_video_instance_id_not_found(
    lyric_service: LyricService,
):
    result = await lyric_service.get_paginated_lyrics(page=1, size=10, video_instance_id=9999)
    assert len(result.items) == 0
    assert result.total == 0


@pytest.mark.asyncio
async def test_lyric_service_get_paginated_lyrics(
    lyric_service: LyricService, normal_lyric: Lyric
):
    # Add several more lyrics for pagination testing
    for i in range(15):  # Adding 15 more lyrics, giving us 16 total with normal_lyric
        await lyric_service.add_lyric(
            AddLyric(
                language=Language.english,
                content=f"Lyric content {i}",
                video_instance_id=1,
            )
        )

    # Test first page with default values (page=1, size=10)
    paginated = await lyric_service.get_paginated_lyrics()
    assert paginated.page == 1
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 10

    # Test second page
    paginated = await lyric_service.get_paginated_lyrics(page=2)
    assert paginated.page == 2
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 6

    # Test with custom page size
    paginated = await lyric_service.get_paginated_lyrics(page=1, size=5)
    assert paginated.page == 1
    assert paginated.size == 5
    assert paginated.total == 16
    assert len(paginated.items) == 5

    # Test with empty page (beyond available data)
    paginated = await lyric_service.get_paginated_lyrics(page=4)
    assert paginated.page == 4
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 0
