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
        async with self._engine.begin() as conn:
            await conn.run_sync(self._base.metadata.create_all)

    async def reset_database(self) -> None:
        """Drop all tables and recreate them.
        Just for testing purposes.
        DO NOT USE IN PRODUCTION
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(self._base.metadata.drop_all)
            await conn.run_sync(self._base.metadata.create_all)
