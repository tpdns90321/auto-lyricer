from ..database import AIOSqlite
from ..shared.supported import Language
from ..video_retrieval import VideoRetrieval
from ..video_retrieval.type import VideoInfo
from ..video.container import VideoContainer
from .container import LyricContainer
from .dto import AddLyric
from .api import router

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Response
from unittest.mock import AsyncMock
from fastapi import FastAPI

normal_video_retrieval = AsyncMock(spec=VideoRetrieval)
normal_video_retrieval.retrieval_video_info.return_value = VideoInfo(
    video_id="testestest",
    domain="youtube.com",
    duration_seconds=100,
    channel_name="channel",
    channel_id="channel_id",
    title="",
    thumbnail_url="thumbnail_url",
)

database = AIOSqlite(relative_path=":memory:")
asyncio.run(database.create_database())
videoContainer = VideoContainer(database=database, retrieval=normal_video_retrieval)
videoContainer.init_resources()
lyricContainer = LyricContainer(database=database)
lyricContainer.init_resources()

app = FastAPI()
app.include_router(router)


@pytest_asyncio.fixture
async def client():
    await database.reset_database()
    await videoContainer.repository().retrieval_video(
        "https://www.youtube.com/watch?v=testestest"
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest_asyncio.fixture
async def add_lyric_success_response(client: AsyncClient) -> Response:
    data: AddLyric = AddLyric(
        video_instance_id=1,
        content="test lyric",
        language=Language.english,
    )
    response = await client.post(
        "/lyric/",
        json={**data.__dict__},
    )
    return response


@pytest.mark.asyncio
async def test_add_lyric_success(add_lyric_success_response: Response):
    response_data = add_lyric_success_response.json()
    print(response_data)
    assert response_data["instance_id"] == 1
    assert response_data["video_instance_id"] == 1
    assert response_data["content"] == "test lyric"
    assert response_data["language"] == Language.english.value


@pytest.mark.asyncio
async def test_add_lyric_invalid_video_instance_id(client: AsyncClient):
    data: AddLyric = AddLyric(
        video_instance_id=999,
        content="test lyric",
        language=Language.english,
    )
    response = await client.post(
        "/lyric/",
        json={**data.__dict__},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_lyric_by_instance_id(
    client: AsyncClient, add_lyric_success_response: Response
):
    response_data = add_lyric_success_response.json()
    instance_id = response_data["instance_id"]
    response = await client.get(f"/lyric/{instance_id}")
    assert response.status_code == 200
    assert response.json()["instance_id"] == instance_id
    assert response.json()["content"] == "test lyric"
    assert response.json()["language"] == Language.english.value


@pytest.mark.asyncio
async def test_get_lyric_by_invalid_instance_id(client: AsyncClient):
    response = await client.get("/lyric/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_list_of_lyrics_by_video_instance_id(
    client: AsyncClient, add_lyric_success_response: Response
):
    response_data = add_lyric_success_response.json()
    video_instance_id = response_data["video_instance_id"]
    response = await client.get(f"/lyric/video/{video_instance_id}")
    assert len(response.json()) == 1
    assert response.json()[0]["instance_id"] == response_data["instance_id"]
    assert response.json()[0]["content"] == "test lyric"
    assert response.json()[0]["language"] == Language.english.value


@pytest.mark.asyncio
async def test_get_list_of_lyrics_by_invalid_video_instance_id(client: AsyncClient):
    response = await client.get("/lyric/video/999")
    assert len(response.json()) == 0
