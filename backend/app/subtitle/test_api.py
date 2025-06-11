from ..database import AIOSqlite
from .container import SubtitleContainer
from .api import router
from ..shared.supported import Language

import asyncio
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
import pytest

from fastapi import FastAPI

database = AIOSqlite(relative_path=":memory:")
container = SubtitleContainer(database=database)
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
async def create_subtitle(client, video_id):
    """Create a sample subtitle and return the response"""
    response = await client.post(
        "/subtitles/",
        json={
            "language": Language.english.value,
            "content": "Test subtitle content",
            "file_format": "srt",
            "video_instance_id": video_id,
        },
    )
    return response


@pytest.mark.asyncio
async def test_create_subtitle(create_subtitle):
    response = create_subtitle
    assert response.status_code == 200

    data = response.json()
    assert data["instance_id"] == 1
    assert data["language"] == Language.english.value
    assert data["content"] == "Test subtitle content"
    assert data["file_format"] == "srt"


@pytest.mark.asyncio
async def test_create_subtitle_with_invalid_video_id(client):
    response = await client.post(
        "/subtitles/",
        json={
            "language": Language.english.value,
            "content": "Test subtitle content",
            "file_format": "srt",
            "video_instance_id": 999,  # Non-existent video ID
        },
    )

    assert response.status_code == 404
    assert "error" in response.json()
    # Rather than checking the exact message, just check that it contains an error
    # message
    assert response.json()["error"]


@pytest.mark.asyncio
async def test_get_subtitle_by_instance_id(client, create_subtitle):
    created_data = create_subtitle.json()

    response = await client.get(f"/subtitles/{created_data['instance_id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["instance_id"] == created_data["instance_id"]
    assert data["language"] == created_data["language"]
    assert data["content"] == created_data["content"]
    assert data["file_format"] == created_data["file_format"]
    assert data["video_instance_id"] == created_data["video_instance_id"]


@pytest.mark.asyncio
async def test_get_subtitle_by_instance_id_not_found(client):
    response = await client.get("/subtitles/999")

    assert response.status_code == 404
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_paginated_subtitles_by_video_instance_id(client, video_id):
    # Create multiple subtitles for the same video
    for i in range(5):
        await client.post(
            "/subtitles/",
            json={
                "language": Language.english.value,
                "content": f"Subtitle {i}",
                "file_format": "srt",
                "video_instance_id": video_id,
            },
        )

    response = await client.get(f"/subtitles/?video_instance_id={video_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert all(subtitle["video_instance_id"] == video_id for subtitle in data["items"])


@pytest.mark.asyncio
async def test_get_paginated_subtitles_by_video_instance_id_not_found(client):
    response = await client.get("/subtitles/?video_instance_id=999")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_paginated_subtitles(client, video_id):
    # Create 15 subtitles for pagination testing
    for i in range(15):
        await client.post(
            "/subtitles/",
            json={
                "language": Language.english.value,
                "content": f"Subtitle {i}",
                "file_format": "srt",
                "video_instance_id": video_id,
            },
        )

    # Test default pagination (page=1, size=10)
    response = await client.get("/subtitles/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 10
    assert len(data["items"]) == 10

    # Test second page
    response = await client.get("/subtitles/?page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 2
    assert data["size"] == 10
    assert len(data["items"]) == 5

    # Test with custom size
    response = await client.get("/subtitles/?size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 5
    assert len(data["items"]) == 5

    # Test with both page and size
    response = await client.get("/subtitles/?page=2&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 2
    assert data["size"] == 5
    assert len(data["items"]) == 5

    # Test with page beyond available data
    response = await client.get("/subtitles/?page=4")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 4
    assert data["size"] == 10
    assert len(data["items"]) == 0

    # Test with invalid parameters (should use defaults)
    response = await client.get("/subtitles/?page=0&size=0")
    assert response.status_code == 422  # FastAPI validation error
