from .AsyncSQLAlchemy import AsyncSQLAlchemy, AsyncSQLAlchemyBase


class AIOSqliteBase(AsyncSQLAlchemyBase):
    __abstract__ = True

    def __init__(self):
        super().__init__()


class AIOSqlite(AsyncSQLAlchemy):
    def __init__(self, relative_path: str):
        super().__init__("sqlite+aiosqlite:///" + relative_path, AIOSqliteBase)


# Below part is imported from another repository's model
from ..video.model import *
