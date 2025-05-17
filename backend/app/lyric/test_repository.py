from ..database import AIOSqlite
from ..shared.supported import Language
from ..video_retrieval.retrieval import VideoRetrieval
from ..video_retrieval.type import VideoInfo
from ..video.repository import VideoRepository
from .repository import LyricRepository
from .dto import AddLyric, Lyric
from .exception import NotFoundThing, NotFoundThingException

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


@pytest_asyncio.fixture
async def normal_lyric(lyric_repository: LyricRepository) -> Lyric:
    return await lyric_repository.add_lyric(
        AddLyric(
            language=Language.english,
            content="Hello, world!",
            video_instance_id=1,
        )
    )


@pytest.mark.asyncio
async def test_lyric_repository_add_lyric(normal_lyric: Lyric):
    assert normal_lyric.instance_id == 1


@pytest.mark.asyncio
async def test_lyric_repository_add_lyric_with_invalid_video(
    lyric_repository: LyricRepository,
):
    with pytest.raises(NotFoundThingException) as notFoundException:
        await lyric_repository.add_lyric(
            AddLyric(
                language=Language.english,
                content="Hello, Bad World!",
                video_instance_id=9999,
            )
        )

    assert notFoundException.value.thing == NotFoundThing.VideoInstance


@pytest.mark.asyncio
async def test_lyric_repository_get_lyric_by_instance_id(
    normal_lyric: Lyric, lyric_repository: LyricRepository
):
    lyric = await lyric_repository.get_lyric_by_instance_id(
        instance_id=normal_lyric.instance_id
    )
    assert lyric is not None
    assert lyric.instance_id == normal_lyric.instance_id
    assert lyric.language == normal_lyric.language
    assert lyric.content == normal_lyric.content


@pytest.mark.asyncio
async def test_lyric_repository_get_lyric_by_instance_id_not_found(
    lyric_repository: LyricRepository,
):
    lyric = await lyric_repository.get_lyric_by_instance_id(instance_id=9999)
    assert lyric is None


@pytest.mark.asyncio
async def test_lyric_repository_get_list_of_lyrics_by_video_instance_id(
    normal_lyric: Lyric, lyric_repository: LyricRepository
):
    lyric2 = await lyric_repository.add_lyric(
        AddLyric(
            language=Language.english,
            content="Hello, world!",
            video_instance_id=1,
        )
    )
    lyrics = await lyric_repository.get_list_of_lyrics_by_video_instance_id(
        video_instance_id=normal_lyric.video_instance_id
    )
    assert len(lyrics) == 2
    assert lyrics[0].instance_id == normal_lyric.instance_id
    assert lyrics[1].instance_id == lyric2.instance_id


@pytest.mark.asyncio
async def test_lyric_repository_get_list_of_lyrics_by_video_instance_id_not_found(
    lyric_repository: LyricRepository,
):
    lyrics = await lyric_repository.get_list_of_lyrics_by_video_instance_id(
        video_instance_id=9999
    )
    assert len(lyrics) == 0


@pytest.mark.asyncio
async def test_lyric_repository_get_paginated_lyrics(
    lyric_repository: LyricRepository, normal_lyric: Lyric
):
    # Add several more lyrics for pagination testing
    for i in range(15):  # Adding 15 more lyrics, giving us 16 total with normal_lyric
        await lyric_repository.add_lyric(
            AddLyric(
                language=Language.english,
                content=f"Lyric content {i}",
                video_instance_id=1,
            )
        )

    # Test first page with default values (page=1, size=10)
    paginated = await lyric_repository.get_paginated_lyrics()
    assert paginated.page == 1
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 10

    # Test second page
    paginated = await lyric_repository.get_paginated_lyrics(page=2)
    assert paginated.page == 2
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 6

    # Test with custom page size
    paginated = await lyric_repository.get_paginated_lyrics(page=1, size=5)
    assert paginated.page == 1
    assert paginated.size == 5
    assert paginated.total == 16
    assert len(paginated.items) == 5

    # Test page beyond available data
    paginated = await lyric_repository.get_paginated_lyrics(page=4)
    assert paginated.page == 4
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 0
