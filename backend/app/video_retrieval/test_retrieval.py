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


@pytest.mark.asyncio
async def test_retrieval_audio_of_video(retrieval: VideoRetrieval):
    audio = await retrieval.retrieval_audio_of_video(
        "https://www.youtube.com/watch?v=LHvYrn3FAgI"
    )
    assert audio is not None
    with open("app/video_retrieval/test_retrieval_audio_of_LHvYrn3FAgI.aac", "rb") as f:
        audio_content = f.read()
        assert audio == audio_content
