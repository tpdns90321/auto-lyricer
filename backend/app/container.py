from .video_retrieval import VideoRetrieval
from .video.container import VideoContainer
from .lyric.container import LyricContainer
from .database import AIOSqlite

from dependency_injector import containers, providers


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_yaml("config.yaml")

    aiosqlite = providers.Singleton(
        AIOSqlite, relative_path=config.aiosqlite.relative_path
    )

    video_retrieval = providers.Singleton(VideoRetrieval, opts=config.yt_dlp.opts)

    video = providers.Container(
        VideoContainer, database=aiosqlite, retrieval=video_retrieval
    )

    lyric = providers.Container(
        LyricContainer,
        database=aiosqlite,
    )
