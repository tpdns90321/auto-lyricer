from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from ..shared.exception import UnknownException
from .model import Lyric as LyricModel
from .dto import Lyric as LyricDTO, AddLyric, PaginatedResponse
from .exception import NotFoundThing, NotFoundThingException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import count


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


    async def get_paginated_lyrics(
        self, page: int = 1, size: int = 10, video_instance_id: int | None = None
    ) -> PaginatedResponse[LyricDTO]:
        async with self._session_factory() as session:
            # Calculate offset based on page and size
            offset = (page - 1) * size

            # Build base query with optional filter
            base_query = Select(LyricModel)
            if video_instance_id is not None:
                base_query = base_query.where(LyricModel.video_instance_id == video_instance_id)

            # Get total count
            total_query = Select(count(LyricModel.instance_id))
            if video_instance_id is not None:
                total_query = total_query.where(LyricModel.video_instance_id == video_instance_id)
            total_result = await session.execute(total_query)
            total = total_result.scalar()
            if total is None:
                total = 0

            # Get paginated results
            query = base_query.limit(size).offset(offset)
            result = await session.execute(query)

            items = [LyricDTO(**model.to_dict()) for model in result.scalars()]

            return PaginatedResponse(items=items, total=total, page=page, size=size)
