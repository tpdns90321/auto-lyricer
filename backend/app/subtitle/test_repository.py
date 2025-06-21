from ..shared.data import SubtitleExtension
from ..shared.supported import Language
from ..database import AIOSqlite
from .exception import NotFoundThingError, NotFoundThing
from .repository import SubtitleRepository
from .dto import Subtitle, CreateSubtitle

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def database() -> AIOSqlite:
    database = AIOSqlite(relative_path=":memory:")
    await database.reset_database()
    return database


@pytest_asyncio.fixture
async def repository(database) -> SubtitleRepository:
    return SubtitleRepository(database=database)


@pytest_asyncio.fixture
async def video_id(database) -> int:
    """Create a test video in the database to use for foreign key constraints"""
    from ..shared.supported import Platform
    from ..video.model import Video

    async with database.session() as session:
        video = Video(
            platform=Platform.youtube,
            video_id="test123",
            channel_id="channel123",
            channel_name="Test Channel",
            title="Test Video",
            duration_seconds=120,
            thumbnail_url="http://example.com/thumbnail.jpg",
        )
        session.add(video)
        await session.commit()
        return video.instance_id


@pytest_asyncio.fixture
async def sample_subtitle(repository, video_id) -> Subtitle:
    dto = CreateSubtitle(
        language=Language.english,
        content="This is a test subtitle",
        video_instance_id=video_id,
        file_format=SubtitleExtension.SRT,
    )
    return await repository.create_subtitle(dto)


@pytest.mark.asyncio
async def test_create_subtitle(repository, video_id):
    dto = CreateSubtitle(
        language=Language.english,
        content="This is a test subtitle",
        video_instance_id=video_id,
        file_format=SubtitleExtension.SRT,
    )

    result = await repository.create_subtitle(dto)

    assert result.instance_id == 1
    assert result.language == Language.english
    assert result.content == "This is a test subtitle"
    assert result.video_instance_id == video_id


@pytest.mark.asyncio
async def test_create_subtitle_with_invalid_video_id(repository):
    dto = CreateSubtitle(
        language=Language.english,
        content="This is a test subtitle",
        file_format=SubtitleExtension.SRT,
        video_instance_id=9999,  # Non-existent video ID
    )

    with pytest.raises(NotFoundThingError) as exc_info:
        await repository.create_subtitle(dto)

    assert exc_info.value.thing == NotFoundThing.VideoInstance


@pytest.mark.asyncio
async def test_get_subtitle_by_instance_id(repository, sample_subtitle):
    result = await repository.get_subtitle_by_instance_id(sample_subtitle.instance_id)

    assert result is not None
    assert result.instance_id == sample_subtitle.instance_id
    assert result.language == sample_subtitle.language
    assert result.content == sample_subtitle.content
    assert result.video_instance_id == sample_subtitle.video_instance_id


@pytest.mark.asyncio
async def test_get_subtitle_by_instance_id_not_found(repository):
    result = await repository.get_subtitle_by_instance_id(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_paginated_subtitles_by_video_instance_id(repository, video_id):
    # Create multiple subtitles for the same video
    for i in range(5):
        dto = CreateSubtitle(
            language=Language.english,
            content=f"Subtitle {i}",
            file_format=SubtitleExtension.SRT,
            video_instance_id=video_id,
        )
        await repository.create_subtitle(dto)

    result = await repository.get_paginated_subtitles(
        page=1, size=10, video_instance_id=video_id
    )

    assert len(result.items) == 5
    assert result.total == 5
    assert all(subtitle.video_instance_id == video_id for subtitle in result.items)


@pytest.mark.asyncio
async def test_get_paginated_subtitles_by_video_instance_id_not_found(repository):
    result = await repository.get_paginated_subtitles(
        page=1, size=10, video_instance_id=999
    )

    assert len(result.items) == 0
    assert result.total == 0


@pytest.mark.asyncio
async def test_get_paginated_subtitles(repository, video_id):
    # Create 15 subtitles for pagination testing
    for i in range(15):
        dto = CreateSubtitle(
            language=Language.english,
            content=f"Subtitle {i}",
            file_format=SubtitleExtension.SRT,
            video_instance_id=video_id,
        )
        await repository.create_subtitle(dto)

    # Test default pagination (page=1, size=10)
    paginated = await repository.get_paginated_subtitles()
    assert paginated.page == 1
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 10

    # Test second page
    paginated = await repository.get_paginated_subtitles(page=2)
    assert paginated.page == 2
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 5

    # Test with custom page size
    paginated = await repository.get_paginated_subtitles(page=1, size=5)
    assert paginated.page == 1
    assert paginated.size == 5
    assert paginated.total == 15
    assert len(paginated.items) == 5

    # Test page beyond available data
    paginated = await repository.get_paginated_subtitles(page=4)
    assert paginated.page == 4
    assert paginated.size == 10
    assert paginated.total == 15
    assert len(paginated.items) == 0
