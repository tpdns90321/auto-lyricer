from dataclasses import dataclass
from enum import Enum


class SupportedPlatform(str, Enum):
    youtube = "youtube"


@dataclass(frozen=True)
class Video:
    instance_id: int
    platform: SupportedPlatform
    video_id: str
    channel_id: str
    channel_name: str
    title: str
    duration_seconds: int
    thumbnail_url: str


@dataclass(frozen=True)
class RetrievalVideo:
    video_url: str
