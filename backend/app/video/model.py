from ..database import AIOSqliteBase
from ..shared.supported import Platform as SupportedPlatform

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..lyric.model import Lyric
    from ..transcription.model import Transcription
    from ..subtitle.model import Subtitle


class Video(AIOSqliteBase):
    __tablename__ = "videos"

    instance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    platform: Mapped[SupportedPlatform]
    video_id: Mapped[str]
    channel_id: Mapped[str]
    channel_name: Mapped[str]
    title: Mapped[str]
    duration_seconds: Mapped[int]
    thumbnail_url: Mapped[str]

    # Relationships
    lyrics: Mapped[list["Lyric"]] = relationship(
        "Lyric",
        back_populates="video",
        init=False,
    )

    transcriptions: Mapped[list["Transcription"]] = relationship(
        "Transcription",
        back_populates="video",
        init=False,
    )

    subtitles: Mapped[list["Subtitle"]] = relationship(
        "Subtitle",
        back_populates="video",
        init=False,
    )

    __table_args__ = (UniqueConstraint("platform", "video_id"),)

    def __repr__(self):
        return f"<Video instance_id={self.instance_id} platform={self.platform} video_id={self.video_id} channel_id={self.channel_id} channel_name={self.channel_name} title={self.title} duration_seconds={self.duration_seconds} thumbnail_url={self.thumbnail_url}>"
