from ..shared.supported import SubtitleExtension

from dataclasses import dataclass
from enum import Enum


class AudioExtension(Enum):
    AAC = "aac"
    MP3 = "mp3"
    OGG = "ogg"
    WAV = "wav"


@dataclass(frozen=True)
class Audio:
    binary: bytes
    extension: AudioExtension


@dataclass(frozen=True)
class Transcription:
    content: str
    extension: SubtitleExtension
