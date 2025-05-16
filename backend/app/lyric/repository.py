from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from ..shared.exception import UnknownException
from .model import Lyric as LyricModel
from .dto import Lyric as LyricDTO, AddLyric
from .exception import NotFoundThing, NotFoundThingException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select


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
            except IntegrityError as e:
                errorMessage = str(e.orig)
                # Have only foriegn key for video instance id, so we can check if it is not found
                if "FOREIGN KEY constraint failed" in errorMessage:
                    raise NotFoundThingException(NotFoundThing.VideoInstance)
                raise UnknownException(e)
            except Exception as e:
                raise UnknownException(e)
            return LyricDTO(**model.to_dict())

    async def get_lyric_by_instance_id(self, instance_id: int) -> LyricDTO | None:
        async with self._session_factory() as session:
            model = await session.get(LyricModel, instance_id)
            if model is None:
                return None
            return LyricDTO(**model.to_dict())

    async def get_list_of_lyrics_by_video_instance_id(
        self, video_instance_id: int
    ) -> list[LyricDTO]:
        async with self._session_factory() as session:
            models = await session.execute(
                Select(LyricModel).where(
                    LyricModel.video_instance_id == video_instance_id
                )
            )
            return [LyricDTO(**model.to_dict()) for model in models.scalars()]
