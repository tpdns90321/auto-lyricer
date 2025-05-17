from ..shared.supported import Language
from ..shared.pagination import *

from dataclasses import dataclass


@dataclass(frozen=True)
class Lyric:
    instance_id: int
    language: Language
    content: str
    video_instance_id: int


@dataclass(frozen=True)
class AddLyric:
    language: Language
    content: str
    video_instance_id: int
