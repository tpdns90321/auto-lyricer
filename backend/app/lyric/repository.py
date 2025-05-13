from ..database.AsyncSQLAlchemy import AsyncSQLAlchemy
from .model import Lyric as LyricModel
from .dto import Lyric as LyricDTO, AddLyric


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
            await session.commit()
            return LyricDTO(**model.to_dict())
