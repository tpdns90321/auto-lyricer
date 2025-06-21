from ..database import AIOSqliteBase
from ..shared.supported import Language
from ..shared.data import SubtitleExtension

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..video.model import Video


class Transcription(AIOSqliteBase):
    __tablename__ = "transcriptions"

    instance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    language: Mapped[Language]
    content: Mapped[str]
    subtitle_extension: Mapped[SubtitleExtension]

    video_instance_id: Mapped[int] = mapped_column(
        ForeignKey("videos.instance_id"),
    )
    video: Mapped["Video"] = relationship(
        "Video",
        foreign_keys=[video_instance_id],
        back_populates="transcriptions",
        init=False,
    )

    def __repr__(self):
        return (
            f"<Transcription instance_id={self.instance_id} language={self.language} "
            f"subtitle_extension={self.subtitle_extension.value} "
            f"video_instance_id={self.video_instance_id}>"
        )
