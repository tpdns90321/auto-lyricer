from ..shared.data import AudioExtension
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
    assert (
        video_info.description
        == """Subscribe to NoCopyrightSounds  👉 http://ncs.lnk.to/SubscribeYouTube

NCS: Music Without Limitations
NCS Spotify: http://spoti.fi/NCS

Free Download / Stream: http://ncs.io/superhero

Connect with NCS:
Snapchat: ncsmusic
• http://soundcloud.com/nocopyrightsounds
• http://instagram.com/nocopyrightsounds
• http://facebook.com/NoCopyrightSounds
• http://twitter.com/NCSounds
• http://spoti.fi/NCS

Unknown Brain
• http://soundcloud.com/UnknownBrain
• http://facebook.com/UnknownBrain

Chris Linton
• http://soundcloud.com/chris-linton-1
• http://facebook.com/chrislintonmusic

NCS YouTube Playlists
NCS Trap http://bit.ly/NCStrap
NCS House http://bit.ly/NCShouse
NCS Dubstep http://bit.ly/NCSdubstep
NCS Drumstep http://bit.ly/NCSdrumstep
NCS Hardstyle http://bit.ly/NCShardstyle
NCS Drum&Bass http://bit.ly/NCSdrumandbass
NCS Electronic Playlist: http://bit.ly/NCSelectronic
ALL NCS MUSIC FULL PLAYLIST: http://bit.ly/ALLNCSmusic

🔑 
🛍 NCS Merchandise → http://ncs.io/StoreID

© Check out our Usage Policy on how to use NCS music in your videos: http://ncs.io/UsagePolicy

To request a commercial license visit: http://ncs.io/Commercial

#UnknownBrain #Superhero #nocopyrightsounds #copyrightfree #music #song #edm #dancemusic #royaltyfreemusic #copyrightfreemusic #nocopyrightmusic #ncs #ncsmusic #electronicmusic #trap"""  # noqa: E501,W291
    )

    assert video_info.domain == "youtube.com"
    assert video_info.channel_id == "UC_aEa8K-EOJ3D6gOs7HcyNg"
    assert video_info.duration_seconds == 182


@pytest.mark.asyncio
async def test_retrieval_audio_of_video(retrieval: VideoRetrieval):
    audio = await retrieval.retrieval_audio_of_video(
        "https://www.youtube.com/watch?v=LHvYrn3FAgI"
    )
    assert audio is not None

    def assert_between_audio_and_file():
        with open(
            "app/video_retrieval/test_retrieval_audio_of_LHvYrn3FAgI.aac", "rb"
        ) as f:
            audio_content = f.read()
            assert audio.binary == audio_content
            assert audio.extension == AudioExtension.AAC

    assert_between_audio_and_file()
