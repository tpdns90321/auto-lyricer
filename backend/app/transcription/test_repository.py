from ..database import AIOSqlite
from ..shared.supported import (
    Language,
    SubtitleExtension,
    Platform as SupportedPlatform,
)
from ..video_retrieval.retrieval import VideoRetrieval
from ..video_retrieval.type import VideoInfo
from ..video.repository import VideoRepository
from .repository import TranscriptionRepository
from .dto import CreateTranscription, Transcription
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
async def transcription_repository(
    database: AIOSqlite, normal_video_retrieval
) -> TranscriptionRepository:
    await VideoRepository(
        database=database,
        retrieval=normal_video_retrieval,
    ).retrieve_and_save_video(platform=SupportedPlatform.youtube, video_id="testestest")
    return TranscriptionRepository(database=database)


@pytest_asyncio.fixture
async def normal_transcription(
    transcription_repository: TranscriptionRepository,
) -> Transcription:
    return await transcription_repository.create_transcription(
        CreateTranscription(
            language=Language.english,
            content="Hello, this is a test transcription!",
            subtitle_extension=SubtitleExtension.SRT,
            video_instance_id=1,
        )
    )


@pytest.mark.asyncio
async def test_transcription_repository_create_transcription(
    normal_transcription: Transcription,
):
    assert normal_transcription.instance_id == 1


@pytest.mark.asyncio
async def test_transcription_repository_create_transcription_with_invalid_video(
    transcription_repository: TranscriptionRepository,
):
    with pytest.raises(NotFoundThingException) as notFoundException:
        await transcription_repository.create_transcription(
            CreateTranscription(
                language=Language.english,
                content="Hello, this is a test transcription!",
                subtitle_extension=SubtitleExtension.SRT,
                video_instance_id=9999,
            )
        )

    assert notFoundException.value.thing == NotFoundThing.VideoInstance


@pytest.mark.asyncio
async def test_transcription_repository_get_transcription_by_instance_id(
    normal_transcription: Transcription,
    transcription_repository: TranscriptionRepository,
):
    transcription = await transcription_repository.get_transcription_by_instance_id(
        instance_id=normal_transcription.instance_id
    )
    assert transcription is not None
    assert transcription.instance_id == normal_transcription.instance_id
    assert transcription.language == normal_transcription.language
    assert transcription.content == normal_transcription.content


@pytest.mark.asyncio
async def test_transcription_repository_get_transcription_by_instance_id_not_found(
    transcription_repository: TranscriptionRepository,
):
    transcription = await transcription_repository.get_transcription_by_instance_id(
        instance_id=9999
    )
    assert transcription is None


@pytest.mark.asyncio
async def test_transcription_repository_get_paginated_transcriptions_by_video_instance_id(
    normal_transcription: Transcription,
    transcription_repository: TranscriptionRepository,
):
    transcription2 = await transcription_repository.create_transcription(
        CreateTranscription(
            language=Language.english,
            content="Another test transcription",
            subtitle_extension=SubtitleExtension.VTT,
            video_instance_id=1,
        )
    )
    result = await transcription_repository.get_paginated_transcriptions(
        page=1, size=10, video_instance_id=normal_transcription.video_instance_id
    )
    assert len(result.items) == 2
    assert result.total == 2
    assert result.items[0].instance_id == normal_transcription.instance_id
    assert result.items[1].instance_id == transcription2.instance_id


@pytest.mark.asyncio
async def test_transcription_repository_get_paginated_transcriptions_by_video_instance_id_not_found(
    transcription_repository: TranscriptionRepository,
):
    result = await transcription_repository.get_paginated_transcriptions(
        page=1, size=10, video_instance_id=9999
    )
    assert len(result.items) == 0
    assert result.total == 0


@pytest.mark.asyncio
async def test_transcription_repository_get_paginated_transcriptions(
    transcription_repository: TranscriptionRepository,
    normal_transcription: Transcription,
):
    # Add several more transcriptions for pagination testing
    for i in range(
        15
    ):  # Adding 15 more transcriptions, giving us 16 total with normal_transcription
        await transcription_repository.create_transcription(
            CreateTranscription(
                language=Language.english,
                content=f"Transcription content {i}",
                subtitle_extension=SubtitleExtension.SRT
                if i % 2 == 0
                else SubtitleExtension.VTT,
                video_instance_id=1,
            )
        )

    # Test first page with default values (page=1, size=10)
    paginated = await transcription_repository.get_paginated_transcriptions()
    assert paginated.page == 1
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 10

    # Test second page
    paginated = await transcription_repository.get_paginated_transcriptions(page=2)
    assert paginated.page == 2
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 6

    # Test with custom page size
    paginated = await transcription_repository.get_paginated_transcriptions(
        page=1, size=5
    )
    assert paginated.page == 1
    assert paginated.size == 5
    assert paginated.total == 16
    assert len(paginated.items) == 5

    # Test page beyond available data
    paginated = await transcription_repository.get_paginated_transcriptions(page=4)
    assert paginated.page == 4
    assert paginated.size == 10
    assert paginated.total == 16
    assert len(paginated.items) == 0
