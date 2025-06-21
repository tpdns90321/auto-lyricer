from .supported import Language

from dataclasses import dataclass, field
from enum import Enum


class AudioExtension(Enum):
    AAC = "aac"
    MP3 = "mp3"
    OGG = "ogg"
    WAV = "wav"


class SubtitleExtension(str, Enum):
    SRT = "srt"
    VTT = "vtt"


@dataclass(frozen=True)
class Audio:
    binary: bytes
    extension: AudioExtension


@dataclass(frozen=True)
class Transcription:
    content: str
    extension: SubtitleExtension
    language: Language | None = field(default=None)
