from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from ..shared.exception import UnknownException
from .model import Transcription as TranscriptionModel
from .dto import (
    Transcription as TranscriptionDTO,
    CreateTranscription,
    PaginatedResponse,
)
from .exception import NotFoundThing, NotFoundThingException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import count


class TranscriptionRepository:
    def __init__(self, database: AsyncSQLAlchemy):
        self._session_factory = database.session

    async def create_transcription(self, dto: CreateTranscription) -> TranscriptionDTO:
        async with self._session_factory() as session:
            model = TranscriptionModel(
                language=dto.language,
                content=dto.content,
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
            return TranscriptionDTO(**model.to_dict())

    async def get_transcription_by_instance_id(
        self, instance_id: int
    ) -> TranscriptionDTO | None:
        async with self._session_factory() as session:
            model = await session.get(TranscriptionModel, instance_id)
            if model is None:
                return None
            return TranscriptionDTO(**model.to_dict())

    async def get_list_of_transcriptions_by_video_instance_id(
        self, video_instance_id: int
    ) -> list[TranscriptionDTO]:
        async with self._session_factory() as session:
            models = await session.execute(
                Select(TranscriptionModel).where(
                    TranscriptionModel.video_instance_id == video_instance_id
                )
            )
            return [TranscriptionDTO(**model.to_dict()) for model in models.scalars()]

    async def get_paginated_transcriptions(
        self, page: int = 1, size: int = 10
    ) -> PaginatedResponse[TranscriptionDTO]:
        async with self._session_factory() as session:
            # Calculate offset based on page and size
            offset = (page - 1) * size

            # Get total count
            total_query = Select(count(TranscriptionModel.instance_id))
            total_result = await session.execute(total_query)
            total = total_result.scalar()
            if total is None:
                total = 0

            # Get paginated results
            query = Select(TranscriptionModel).limit(size).offset(offset)
            result = await session.execute(query)

            items = [TranscriptionDTO(**model.to_dict()) for model in result.scalars()]

            return PaginatedResponse(items=items, total=total, page=page, size=size)
