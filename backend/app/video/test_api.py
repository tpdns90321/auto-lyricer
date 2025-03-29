from ..database import AIOSqlite
from ..video_retrieval import VideoRetrieval
from ..video_retrieval.type import VideoInfo
from .container import VideoContainer
from .api import router
from .dto import SupportedPlatform, Video

import asyncio
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Response
import pytest
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
container = VideoContainer(database=database, retrieval=normal_video_retrieval)
container.init_resources()
asyncio.run(database.create_database())

app = FastAPI()
app.include_router(router)


@pytest_asyncio.fixture
async def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest_asyncio.fixture
async def video_retrieval_success_response(client: AsyncClient):
    response = await client.post(
        "/video/retrieval",
        json={"video_url": "https://www.youtube.com/watch?v=testestest"},
    )
    return response


def _response_to_video(response: Response) -> Video:
    response_json = response.json()
    return Video(
        **{
            **response_json,
            "platform": SupportedPlatform.youtube,
            "duration_seconds": int(response_json["duration_seconds"]),
        }
    )


@pytest.mark.asyncio
async def test_retrieval_video_normal(video_retrieval_success_response: Response):
    response_data = _response_to_video(video_retrieval_success_response)
    assert response_data.instance_id == 1
    assert response_data.platform == SupportedPlatform.youtube
    assert response_data.video_id == "testestest"
    assert response_data.channel_name == "channel"
    assert response_data.channel_id == "channel_id"
    assert response_data.duration_seconds == 100
    assert response_data.thumbnail_url == "thumbnail_url"


@pytest.mark.asyncio
async def test_retrieval_video_duplicated(
    video_retrieval_success_response: Response, client: AsyncClient
):
    previous_response_data = _response_to_video(video_retrieval_success_response)
    response = await client.post(
        "/video/retrieval",
        json={"video_url": "https://www.youtube.com/watch?v=testestest"},
    )
    assert response.status_code == 200
    current_response_data = _response_to_video(response)

    assert current_response_data.instance_id == 1
    assert previous_response_data.video_id == current_response_data.video_id
