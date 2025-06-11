from ..database import AIOSqliteBase
from ..shared.supported import Language, SubtitleExtension

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..video.model import Video


class Subtitle(AIOSqliteBase):
    __tablename__ = "subtitles"

    instance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    language: Mapped[Language]
    content: Mapped[str]
    file_format: Mapped[SubtitleExtension]

    video_instance_id: Mapped[int] = mapped_column(
        ForeignKey("videos.instance_id"),
    )
    video: Mapped["Video"] = relationship(
        "Video",
        foreign_keys=[video_instance_id],
        back_populates="subtitles",
        init=False,
    )

    def __repr__(self):
        return (
            f"<Subtitle instance_id={self.instance_id} language={self.language} "
            f"file_format={self.file_format.value} "
            f"video_instance_id={self.video_instance_id}>"
        )
