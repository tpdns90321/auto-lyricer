from .repository import TranscriptionRepository
from .service import TranscriptionService

from dependency_injector import containers, providers


class TranscriptionContainer(containers.DeclarativeContainer):
    # Dependencies injected from parent container
    database = providers.Dependency()

    # Repository
    repository = providers.Factory(
        TranscriptionRepository,
        database=database.provided,
    )

    # Service
    service = providers.Factory(
        TranscriptionService,
        repository=repository,
    )

    wiring_config = containers.WiringConfiguration(
        modules=[".api"],
    )
