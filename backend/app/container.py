from database import AIOSqlite
from video.container import VideoContainer

from dependency_injector import containers, providers


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_yaml("config.yaml")

    aiosqlite = providers.Singleton(
        AIOSqlite, relative_path=config.aiosqlite.relative_path
    )

    video = providers.Container(VideoContainer, database=aiosqlite)
