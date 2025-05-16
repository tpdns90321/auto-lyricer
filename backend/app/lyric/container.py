from .repository import LyricRepository
from .service import LyricService

from dependency_injector import containers, providers


class LyricContainer(containers.DeclarativeContainer):
    database = providers.Dependency()

    repository = providers.Factory(LyricRepository, database=database.provided)

    service = providers.Factory(LyricService, lyric_repository=repository.provided)

    wiring_config = containers.WiringConfiguration(
        modules=[".api"],
    )
