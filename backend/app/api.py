from .container import AppContainer
from .video.api import router as video_router
from .lyric.api import router as lyric_router

from contextlib import asynccontextmanager
from fastapi import FastAPI

container = AppContainer()
container.wire(modules=[__name__])


@asynccontextmanager
async def lifespan(_: FastAPI):
    container.init_resources()
    await container.aiosqlite().create_database()
    yield


api = FastAPI(lifespan=lifespan)

api.include_router(video_router)
api.include_router(lyric_router)
