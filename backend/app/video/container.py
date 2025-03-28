from .repository import VideoRepository
from app.database import AsyncSQLAlchemy

from dependency_injector import containers, providers


class VideoContainer(containers.DeclarativeContainer):
    database = providers.Dependency()
    databaseInstance: AsyncSQLAlchemy = database.provided()

    repository = providers.Factory(
        VideoRepository,
        database=databaseInstance,
    )
