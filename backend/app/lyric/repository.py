from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from .model import Lyric as LyricModel
from .dto import Lyric as LyricDTO, AddLyric
from .exception import NotFoundThing, NotFoundThingException

from sqlalchemy.exc import IntegrityError


class LyricRepository:
    def __init__(self, database: AsyncSQLAlchemy):
        self._session_factory = database.session

    async def add_lyric(self, dto: AddLyric) -> LyricDTO:
        async with self._session_factory() as session:
            model = LyricModel(
                language=dto.language,
                content=dto.content,
                video_instance_id=dto.video_instance_id,
            )
            session.add(model)
            try:
                await session.commit()
            except IntegrityError:
                raise NotFoundThingException(NotFoundThing.VideoInstance)
            return LyricDTO(**model.to_dict())
