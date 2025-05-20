from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from ..shared.exception import UnknownException
from .model import Subtitle as SubtitleModel
from .dto import (
    Subtitle as SubtitleDTO,
    CreateSubtitle,
    PaginatedResponse,
)
from .exception import NotFoundThing, NotFoundThingException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import count


class SubtitleRepository:
    def __init__(self, database: AsyncSQLAlchemy):
        self._session_factory = database.session

    async def create_subtitle(self, dto: CreateSubtitle) -> SubtitleDTO:
        async with self._session_factory() as session:
            model = SubtitleModel(
                language=dto.language,
                content=dto.content,
                file_format=dto.file_format,
                video_instance_id=dto.video_instance_id,
            )
            session.add(model)
            try:
                await session.commit()
            except IntegrityError as e:
                error_message = str(e.orig)
                # Check if it's a foreign key constraint failure
                if "FOREIGN KEY constraint failed" in error_message:
                    raise NotFoundThingException(NotFoundThing.VideoInstance)
                raise UnknownException(e)
            except Exception as e:
                raise UnknownException(e)
            return SubtitleDTO(**model.to_dict())

    async def get_subtitle_by_instance_id(self, instance_id: int) -> SubtitleDTO | None:
        async with self._session_factory() as session:
            model = await session.get(SubtitleModel, instance_id)
            if model is None:
                return None
            return SubtitleDTO(**model.to_dict())

    async def get_list_of_subtitles_by_video_instance_id(
        self, video_instance_id: int
    ) -> list[SubtitleDTO]:
        async with self._session_factory() as session:
            models = await session.execute(
                Select(SubtitleModel).where(
                    SubtitleModel.video_instance_id == video_instance_id
                )
            )
            return [SubtitleDTO(**model.to_dict()) for model in models.scalars()]

    async def get_paginated_subtitles(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[SubtitleDTO]:
        async with self._session_factory() as session:
            # Calculate offset based on page and size
            offset = (page - 1) * size

            # Get total count
            total_query = Select(count(SubtitleModel.instance_id))
            total_result = await session.execute(total_query)
            total = total_result.scalar()
            if total is None:
                total = 0

            # Get paginated results
            query = Select(SubtitleModel).limit(size).offset(offset)
            result = await session.execute(query)

            items = [SubtitleDTO(**model.to_dict()) for model in result.scalars()]

            return PaginatedResponse(items=items, total=total, page=page, size=size)
