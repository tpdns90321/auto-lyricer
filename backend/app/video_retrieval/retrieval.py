from .monkey_patch import gevent
import yt_dlp
import asyncio_gevent

from .type import VideoInfo
from .exception import VideoExtractError


class VideoRetrieval:
    def __init__(self, opts: dict):
        self._opts = opts

    async def retrieval_video_info(self, url: str) -> VideoInfo:
        def _retrieval_video_info() -> VideoInfo:
            with yt_dlp.YoutubeDL(self._opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise VideoExtractError("Cannot extract video info")

                return VideoInfo(
                    video_id=info.get("display_id", ""),
                    domain=info.get("webpage_url_domain", ""),
                    duration_seconds=info.get("duration", 0),
                    channel_name=info.get("uploader", ""),
                    channel_id=info.get("channel_id", ""),
                    title=info.get("title", ""),
                    thumbnail_url=info.get("thumbnail", ""),
                )

        result: VideoInfo = await asyncio_gevent.greenlet_to_future(
            gevent.spawn(_retrieval_video_info)
        )
        return result
