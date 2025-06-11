from ..shared.supported import Language
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Lyric:
    """Represents a lyric associated with a video."""

    instance_id: int = field(
        metadata={
            "description": "Unique lyric record ID.",
            "example": 1,
        }
    )
    language: Language = field(
        metadata={
            "description": "Language code for the lyric.",
            "example": "en",
        }
    )
    content: str = field(
        metadata={
            "description": "Lyric text content.",
            "example": "Let it be, let it be, let it be, let it be...",
        }
    )
    video_instance_id: int = field(
        metadata={
            "description": "ID of the associated video entry.",
            "example": 10,
        }
    )


@dataclass(frozen=True)
class AddLyric:
    """Request schema for creating a new lyric."""

    language: Language = field(
        metadata={
            "description": "Language code for the lyric.",
            "example": "en",
        }
    )
    content: str = field(
        metadata={
            "description": "Lyric text content.",
            "example": "Here comes the sun...",
        }
    )
    video_instance_id: int = field(
        metadata={
            "description": "ID of the associated video entry.",
            "example": 10,
        }
    )
