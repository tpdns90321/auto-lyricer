from .container import VideoContainer
from .service import VideoService
from .dto import RetrievalVideo, SupportedPlatform, Video, PaginatedResponse

from fastapi.routing import APIRouter
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/retrieval")
@inject
async def retrieval(
    dto: RetrievalVideo,
    service: VideoService = Depends(Provide[VideoContainer.service]),
) -> Video:
    return await service.retrieval_video(dto)


@router.get(
    "/video_id/{platform}/{video_id}",
    response_model=Video,
    responses={404: {"description": "Not found"}},
)
@inject
async def get_video_by_video_id(
    platform: SupportedPlatform,
    video_id: str,
    service: VideoService = Depends(Provide[VideoContainer.service]),
) -> Video | JSONResponse:
    result = await service.get_video_by_video_id(SupportedPlatform(platform), video_id)
    if result is None:
        # return None with 404 status code
        return JSONResponse(content=None, status_code=status.HTTP_404_NOT_FOUND)

    return result


@router.get(
    "/instance_id/{instance_id}",
    response_model=Video,
    responses={404: {"description": "Not found"}},
)
@inject
async def get_video_by_instance_id(
    instance_id: int,
    service: VideoService = Depends(Provide[VideoContainer.service]),
) -> Video | JSONResponse:
    result = await service.get_video_by_instance_id(instance_id)
    if result is None:
        # return None with 404 status code
        return JSONResponse(content=None, status_code=status.HTTP_404_NOT_FOUND)

    return result


@router.get(
    "/",
    response_model=PaginatedResponse[Video],
)
@inject
async def get_videos(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: VideoService = Depends(Provide[VideoContainer.service]),
) -> PaginatedResponse[Video]:
    """Get paginated list of videos.

    - **page**: Page number (starting from 1)
    - **size**: Items per page (1-100, default 10)
    """
    return await service.get_paginated_videos(page, size)
