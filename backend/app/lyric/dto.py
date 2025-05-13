from dataclasses import dataclass


@dataclass(frozen=True)
class Lyric:
    instance_id: int
    language: str
    content: str
    video_instance_id: int


@dataclass(frozen=True)
class AddLyric:
    language: str
    content: str
    video_instance_id: int
