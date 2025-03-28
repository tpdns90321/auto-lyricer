from dataclasses import dataclass


@dataclass(frozen=True)
class VideoInfo:
    video_id: str
    domain: str
    duration_seconds: int
    channel_name: str
    channel_id: str
    title: str
    thumbnail_url: str
