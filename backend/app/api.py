from .container import AppContainer
from .video.api import router as video_router
from .lyric.api import router as lyric_router
from .transcription.api import router as transcription_router
from .subtitle.api import router as subtitle_router

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

container = AppContainer()


@asynccontextmanager
async def lifespan(_: FastAPI):
    container.init_resources()
    await container.aiosqlite().create_database()
    yield


api = FastAPI(
    title="Auto Lyricer Backend API",
    description="API for video, lyrics, transcription, and subtitle operations.",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Auto Lyricer",
        "url": "https://github.com/tpdns90321/auto-lyricer",
    },
    license_info={
        "name": "AGPL-3.0",
        "url": "https://github.com/tpdns90321/auto-lyricer/blob/main/LICENSE",
    },
)

# CORS Middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging Middleware
@api.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("api")
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed with status: {response.status_code}")
    return response


# Error handler for unhandled exceptions
@api.exception_handler(Exception)
async def unicorn_exception_handler(_: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# API Versioning: prefix all routers with /api/v1
api.include_router(video_router, prefix="/api/v1")
api.include_router(lyric_router, prefix="/api/v1")
api.include_router(transcription_router, prefix="/api/v1")
api.include_router(subtitle_router, prefix="/api/v1")


# Health Check Endpoint
@api.get("/api/v1/health", tags=["health"])
async def health_check():
    return JSONResponse("OK", status_code=200)
