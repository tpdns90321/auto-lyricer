from ..shared.supported import SubtitleExtension

from dataclasses import dataclass
from enum import Enum


class AudioExtension(Enum):
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    M4A = "m4a"


@dataclass(frozen=True)
class Audio:
    binary: bytes
    extension: AudioExtension


@dataclass(frozen=True)
class Transcription:
    content: str
    extension: SubtitleExtension
