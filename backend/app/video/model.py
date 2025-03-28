from app.database import AIOSqliteBase
from sqlalchemy.orm import Mapped, mapped_column


class Video(AIOSqliteBase):
    __tablename__ = "videos"

    instance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    platform: Mapped[str]
    video_id: Mapped[str]
    channel_id: Mapped[str]
    channel_name: Mapped[str]
    title: Mapped[str]
    duration_seconds: Mapped[int]
    thumbnail_url: Mapped[str]

    def __repr__(self):
        return f"<Video instance_id={self.instance_id} platform={self.platform} video_id={self.video_id} channel_id={self.channel_id} channel_name={self.channel_name} title={self.title} duration_seconds={self.duration_seconds} thumbnail_url={self.thumbnail_url}>"
