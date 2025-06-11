from .model import SupportedPlatform
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Video:
    """Represents a video entity."""

    instance_id: int = field(
        metadata={
            "description": "Unique video record ID.",
            "example": 1,
        }
    )
    platform: SupportedPlatform = field(
        metadata={
            "description": "Video platform (e.g., youtube).",
            "example": "youtube",
        }
    )
    video_id: str = field(
        metadata={
            "description": "Platform-specific video ID.",
            "example": "dQw4w9WgXcQ",
        }
    )
    channel_id: str = field(
        metadata={
            "description": "Channel ID the video belongs to.",
            "example": "UC38IQsAvIsxxjztdMZQtwHA",
        }
    )
    channel_name: str = field(
        metadata={
            "description": "Name of the video channel.",
            "example": "RickAstleyVEVO",
        }
    )
    title: str = field(
        metadata={
            "description": "The video's title.",
            "example": "Never Gonna Give You Up",
        }
    )
    duration_seconds: int = field(
        metadata={
            "description": "Duration in seconds.",
            "example": 212,
        }
    )
    thumbnail_url: str = field(
        metadata={
            "description": "Thumbnail image URL.",
            "example": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        }
    )


@dataclass(frozen=True)
class RetrievalVideo:
    """Request schema for video retrieval by URL."""

    video_url: str = field(
        metadata={
            "description": "URL of the video to retrieve.",
            "example": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
    )
