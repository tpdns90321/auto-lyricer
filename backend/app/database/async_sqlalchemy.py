import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class AsyncSQLAlchemyBase(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    __table_args__ = {"keep_existing": True}

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class AsyncSQLAlchemy:
    def __init__(self, connection_url: str, base: type[DeclarativeBase]):
        """Initialize AsyncSQLAlchemy with connection URL and base class.

        Args:
            connection_url: Database connection URL.
            base: SQLAlchemy declarative base class.
        """
        self._connection_url = connection_url
        self._engine = create_async_engine(connection_url, echo=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False,
            ),
            scopefunc=asyncio.current_task,
        )
        self._base = base

    @asynccontextmanager
    async def session(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_database(self) -> None:
        # Ensure all models are imported before creating tables
        self._register_models()
        async with self._engine.begin() as conn:
            await conn.run_sync(self._base.metadata.create_all)

    def _register_models(self) -> None:
        """Import all models to register them with SQLAlchemy."""
        try:
            from ..lyric.model import Lyric  # noqa: F401 # type: ignore
            from ..subtitle.model import Subtitle  # noqa: F401 # type: ignore
            from ..transcription.model import Transcription  # noqa: F401 # type: ignore
            from ..video.model import Video  # noqa: F401 # type: ignore
        except ImportError:
            # Models might not be available in all contexts (e.g., during testing)
            pass

    async def reset_database(self) -> None:
        """Drop all tables and recreate them.

        Just for testing purposes.
        DO NOT USE IN PRODUCTION
        """
        # Ensure all models are imported before operating on tables
        self._register_models()
        async with self._engine.begin() as conn:
            await conn.run_sync(self._base.metadata.drop_all)
            await conn.run_sync(self._base.metadata.create_all)
