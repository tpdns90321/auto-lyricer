from .retrieval import VideoRetrieval

import pytest


@pytest.fixture
def retrieval() -> VideoRetrieval:
    return VideoRetrieval({})


@pytest.mark.asyncio
async def test_retrieval_video_info(retrieval: VideoRetrieval):
    video_info = await retrieval.retrieval_video_info(
        "https://www.youtube.com/watch?v=LHvYrn3FAgI"
    )
    assert video_info.video_id == "LHvYrn3FAgI"
    assert video_info.domain == "youtube.com"
    assert video_info.channel_id == "UC_aEa8K-EOJ3D6gOs7HcyNg"
    assert video_info.duration_seconds == 182
