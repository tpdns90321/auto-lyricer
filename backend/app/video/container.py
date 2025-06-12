from .repository import VideoRepository
from .service import VideoService

from dependency_injector import containers, providers


class VideoContainer(containers.DeclarativeContainer):
    database = providers.Dependency()
    retrieval = providers.Dependency()

    repository = providers.Factory(
        VideoRepository,
        database=database.provided,
    )

    service = providers.Factory(
        VideoService,
        repository=repository.provided,
        retrieval=retrieval.provided,
    )

    wiring_config = containers.WiringConfiguration(
        modules=[".api"],
    )
