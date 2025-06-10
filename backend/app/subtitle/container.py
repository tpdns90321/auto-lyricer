from .repository import SubtitleRepository
from .service import SubtitleService

from dependency_injector import containers, providers


class SubtitleContainer(containers.DeclarativeContainer):
    # Dependencies injected from parent container
    database = providers.Dependency()

    # Repository
    repository = providers.Factory(
        SubtitleRepository,
        database=database.provided,
    )

    # Service
    service = providers.Factory(
        SubtitleService,
        repository=repository,
    )

    wiring_config = containers.WiringConfiguration(
        modules=[".api"],
    )
