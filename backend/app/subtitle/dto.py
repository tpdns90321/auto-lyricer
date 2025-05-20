from ..shared.supported import Language
from ..shared.pagination import *
from .type import FileFormat

from dataclasses import dataclass


@dataclass(frozen=True)
class Subtitle:
    instance_id: int
    language: Language
    content: str
    file_format: FileFormat
    video_instance_id: int


@dataclass(frozen=True)
class CreateSubtitle:
    language: Language
    content: str
    file_format: FileFormat
    video_instance_id: int
