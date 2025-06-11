from ..shared.supported import Language, SubtitleExtension
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Transcription:
    """Represents a transcription entry for a video."""

    instance_id: int = field(
        metadata={"description": "Unique transcription record ID.", "example": 1}
    )
    language: Language = field(
        metadata={"description": "Transcription language code.", "example": "ko"}
    )
    content: str = field(
        metadata={
            "description": "Transcription content/text.",
            "example": "절대 널 포기하지 않을 거야...",
        }
    )
    subtitle_extension: SubtitleExtension = field(
        metadata={"description": "Subtitle file format.", "example": "srt"}
    )
    video_instance_id: int = field(
        metadata={"description": "Associated video instance ID.", "example": 1}
    )


@dataclass(frozen=True)
class CreateTranscription:
    """Request schema for creating a new transcription."""

    language: Language = field(
        metadata={"description": "Transcription language code.", "example": "ko"}
    )
    content: str = field(
        metadata={
            "description": "Transcription content/text.",
            "example": "절대 널 포기하지 않을 거야...",
        }
    )
    subtitle_extension: SubtitleExtension = field(
        metadata={"description": "Subtitle file format.", "example": "vtt"}
    )
    video_instance_id: int = field(
        metadata={"description": "Associated video instance ID.", "example": 1}
    )
