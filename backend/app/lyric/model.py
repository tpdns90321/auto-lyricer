from sqlalchemy.sql.schema import ForeignKey

from ..database import AIOSqliteBase
from ..shared.supported import Language

from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..video.model import Video


class Lyric(AIOSqliteBase):
    __tablename__ = "lyrics"

    instance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    language: Mapped[Language]
    content: Mapped[str]

    video_instance_id: Mapped[int] = mapped_column(
        ForeignKey("videos.instance_id"),
    )
    video: Mapped["Video"] = relationship(
        "Video",
        foreign_keys=[video_instance_id],
        back_populates="lyrics",
        init=False,
    )

    def __repr__(self):
        return (
            f"<Lyric instance_id={self.instance_id} content={self.content} "
            f"language={self.language} video_instance_id={self.video_instance_id}>"
        )
