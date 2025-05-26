
from ..shared.supported import Language, SubtitleExtension
from ..shared.pagination import *
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Subtitle:
    """Represents a subtitle entry for a video."""
    instance_id: int = field(
        metadata={"description": "Unique subtitle record ID.", "example": 1}
    )
    language: Language = field(
        metadata={"description": "Subtitle language code.", "example": "en"}
    )
    content: str = field(
        metadata={"description": "Subtitle content/text.", "example": "[Music] Never gonna give you up..."}
    )
    file_format: SubtitleExtension = field(
        metadata={"description": "Subtitle file format.", "example": "srt"}
    )
    video_instance_id: int = field(
        metadata={"description": "Associated video instance ID.", "example": 1}
    )


@dataclass(frozen=True)
class CreateSubtitle:
    """Request schema for creating a new subtitle entry."""
    language: Language = field(
        metadata={"description": "Subtitle language code.", "example": "ja"}
    )
    content: str = field(
        metadata={"description": "Subtitle content/text.", "example": "[音楽] 君を諦めない..."}
    )
    file_format: SubtitleExtension = field(
        metadata={"description": "Subtitle file format.", "example": "vtt"}
    )
    video_instance_id: int = field(
        metadata={"description": "Associated video instance ID.", "example": 1}
    )
