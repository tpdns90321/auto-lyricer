from .AsyncSQLAlchemy import AsyncSQLAlchemy, AsyncSQLAlchemyBase
from sqlalchemy import event


class AIOSqliteBase(AsyncSQLAlchemyBase):
    __abstract__ = True

    def __init__(self):
        super().__init__()


class AIOSqlite(AsyncSQLAlchemy):
    def __init__(self, relative_path: str):
        super().__init__("sqlite+aiosqlite:///" + relative_path, AIOSqliteBase)
        event.listen(self._engine.sync_engine, "connect", self._enable_foreign_keys)

    def _enable_foreign_keys(self, dbapi_conn, _):
        """Enable foreign keys for SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
