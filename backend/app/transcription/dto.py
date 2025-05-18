from ..shared.supported import Language
from ..shared.pagination import *

from dataclasses import dataclass


@dataclass(frozen=True)
class Transcription:
    instance_id: int
    language: Language
    content: str
    video_instance_id: int


@dataclass(frozen=True)
class CreateTranscription:
    language: Language
    content: str
    video_instance_id: int