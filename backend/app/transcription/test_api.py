from ..database import AIOSqlite
from ..shared.supported import Language, Platform
from ..shared.data import SubtitleExtension
from .container import TranscriptionContainer
from .dto import CreateTranscription
from .api import router

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Response
from fastapi import FastAPI
from dataclasses import asdict

database = AIOSqlite(relative_path=":memory:")
container = TranscriptionContainer(database=database)
container.init_resources()
asyncio.run(database.create_database())

app = FastAPI()
app.include_router(router)


@pytest_asyncio.fixture
async def client():
    await database.reset_database()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest_asyncio.fixture
async def video_id():
    """Create a test video in the database to use for foreign key constraints"""
    from ..video.model import Video

    async with database.session() as session:
        video = Video(
            platform=Platform.youtube,
            video_id="testestest",
            channel_id="channel123",
            channel_name="Test Channel",
            title="Test Video",
            duration_seconds=100,
            thumbnail_url="http://example.com/thumbnail.jpg",
        )
        session.add(video)
        await session.commit()
        return video.instance_id


@pytest_asyncio.fixture
async def create_transcription_success_response(
    client: AsyncClient, video_id: int
) -> Response:
    data: CreateTranscription = CreateTranscription(
        video_instance_id=video_id,
        content="test transcription",
        language=Language.english,
        subtitle_extension=SubtitleExtension.SRT,
    )
    response = await client.post(
        "/transcription/",
        json=asdict(data),
    )
    return response


@pytest.mark.asyncio
async def test_create_transcription_success(
    create_transcription_success_response: Response,
):
    if create_transcription_success_response.status_code != 200:
        print(f"Response status: {create_transcription_success_response.status_code}")
        print(f"Response body: {create_transcription_success_response.text}")
    assert create_transcription_success_response.status_code == 200
    response_data = create_transcription_success_response.json()
    assert response_data["instance_id"] == 1
    assert response_data["video_instance_id"] >= 1
    assert response_data["content"] == "test transcription"
    assert response_data["language"] == Language.english.value
    assert response_data["subtitle_extension"] == SubtitleExtension.SRT.value


@pytest.mark.asyncio
async def test_create_transcription_invalid_video_instance_id(client: AsyncClient):
    data: CreateTranscription = CreateTranscription(
        video_instance_id=999,
        content="test transcription",
        language=Language.english,
        subtitle_extension=SubtitleExtension.SRT,
    )
    response = await client.post(
        "/transcription/",
        json=asdict(data),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transcription_by_instance_id(
    client: AsyncClient, create_transcription_success_response: Response
):
    response_data = create_transcription_success_response.json()
    instance_id = response_data["instance_id"]
    response = await client.get(f"/transcription/{instance_id}")
    assert response.status_code == 200
    assert response.json()["instance_id"] == instance_id
    assert response.json()["content"] == "test transcription"
    assert response.json()["language"] == Language.english.value
    assert response.json()["subtitle_extension"] == SubtitleExtension.SRT.value


@pytest.mark.asyncio
async def test_get_transcription_by_invalid_instance_id(client: AsyncClient):
    response = await client.get("/transcription/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_paginated_transcriptions_by_video_instance_id(
    client: AsyncClient, create_transcription_success_response: Response
):
    response_data = create_transcription_success_response.json()
    video_instance_id = response_data["video_instance_id"]
    response = await client.get(
        f"/transcription/?video_instance_id={video_instance_id}"
    )
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["instance_id"] == response_data["instance_id"]
    assert data["items"][0]["content"] == "test transcription"
    assert data["items"][0]["language"] == Language.english.value


@pytest.mark.asyncio
async def test_get_paginated_transcriptions_by_invalid_video_instance_id(
    client: AsyncClient,
):
    response = await client.get("/transcription/?video_instance_id=999")
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_paginated_transcriptions(client: AsyncClient, video_id: int):
    # Add 15 more transcriptions
    for i in range(15):
        data = CreateTranscription(
            video_instance_id=video_id,
            content=f"paginated transcription {i}",
            language=Language.english,
            subtitle_extension=SubtitleExtension.VTT,
        )
        await client.post("/transcription/", json=asdict(data))

    # Test default pagination (page=1, size=10)
    response = await client.get("/transcription/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 10
    assert len(data["items"]) == 10

    # Test with page parameter
    response = await client.get("/transcription/?page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 2
    assert data["size"] == 10
    assert len(data["items"]) == 5

    # Test with custom size
    response = await client.get("/transcription/?size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 5
    assert len(data["items"]) == 5

    # Test with both page and size
    response = await client.get("/transcription/?page=2&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 2
    assert data["size"] == 5
    assert len(data["items"]) == 5

    # Test with page beyond available data
    response = await client.get("/transcription/?page=4")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 4
    assert data["size"] == 10
    assert len(data["items"]) == 0

    # Test with invalid parameters (should use defaults)
    response = await client.get("/transcription/?page=0&size=0")
    assert response.status_code == 422  # FastAPI validation error
