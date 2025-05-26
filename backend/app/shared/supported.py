from enum import Enum


class Platform(str, Enum):
    youtube = "youtube"


class Language(str, Enum):
    # Language codes are taken from ISO 639-1
    english = "en"
    japanese = "ja"
    korean = "ko"


class SubtitleExtension(str, Enum):
    SRT = "srt"
    VTT = "vtt"
