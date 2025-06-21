from ..shared.data import Audio, AudioExtension, SubtitleExtension, Transcription
from ..shared.supported import Language
from ..shared.exception import UnsupportedPlatformError
from .monkey_patch import gevent
from .type import VideoInfo
from .exception import VideoExtractError

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
import asyncio
import asyncio_gevent
from urllib.parse import urlparse


class VideoRetrieval:
    def __init__(self, opts: dict):
        """Initialize VideoRetrieval with yt-dlp options.

        Args:
            opts: Dictionary of yt-dlp options for video extraction.
        """
        self._opts = opts

    async def retrieval_video_info(self, url: str) -> VideoInfo:
        def _retrieval_video_info() -> VideoInfo:
            with yt_dlp.YoutubeDL(self._opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise VideoExtractError("Cannot extract video info")

                return VideoInfo(
                    video_id=info.get("display_id", ""),
                    description=info.get("description", ""),
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

    async def retrieval_audio_of_video(self, url: str) -> Audio:
        ytd_process = await asyncio.subprocess.create_subprocess_exec(
            "yt-dlp",
            "-f",
            "bestaudio",
            url,
            "--no-warnings",
            "--quiet",
            "-o",
            "-",
            stdout=asyncio.subprocess.PIPE,
        )

        if ytd_process.stdout is None:
            raise VideoExtractError("Cannot extract video audio")

        binary = await ytd_process.stdout.read()
        return Audio(
            binary=binary,
            extension=AudioExtension.AAC,
        )

    async def retrieval_subtitle_of_video(
        self, url: str, target_language: Language | None = None
    ) -> Transcription:
        parsed_url = urlparse(url)
        hostname: str = parsed_url.hostname or ""
        video_id = ""
        if (
            "youtube.com" in hostname
            and parsed_url.path.startswith("/watch")
            and "v=" in parsed_url.query
        ):
            video_id = parsed_url.query.split("v=")[-1].split("&")[0]
        elif (
            "youtu.be" in hostname
            and parsed_url.path.startswith("/")
            and len(parsed_url.path) > 1  # Ensure there's a video ID
        ):
            video_id = parsed_url.path[1:]
        else:
            hostname: str = parsed_url.hostname or ""
            raise UnsupportedPlatformError(hostname)

        def _retrieval_subtitle_of_video_from_youtube() -> Transcription:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            transcript = transcript_list.find_transcript(
                [lang.value for lang in Language]
                if target_language is None
                else [target_language.value]
            )
            language = Language(transcript.language_code)
            fetched_transcription = transcript.fetch()

            formatter = WebVTTFormatter()
            result = formatter.format_transcript(fetched_transcription)
            return Transcription(
                content=result, extension=SubtitleExtension.VTT, language=language
            )

        result = await asyncio_gevent.greenlet_to_future(
            gevent.spawn(_retrieval_subtitle_of_video_from_youtube)
        )
        return result
