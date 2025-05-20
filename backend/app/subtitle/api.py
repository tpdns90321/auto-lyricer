from .container import SubtitleContainer
from .service import SubtitleService
from .dto import CreateSubtitle, Subtitle, PaginatedResponse

from fastapi.routing import APIRouter
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/subtitles", tags=["subtitles"])


@router.post("/", response_model=Subtitle, responses={404: {"description": "Not found"}})
@inject
async def create_subtitle(
    dto: CreateSubtitle,
    service: SubtitleService = Depends(Provide[SubtitleContainer.service]),
) -> Subtitle | JSONResponse:
    try:
        return await service.create_subtitle(dto)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{instance_id}",
    response_model=Subtitle,
    responses={404: {"description": "Not found"}},
)
@inject
async def get_subtitle_by_instance_id(
    instance_id: int,
    service: SubtitleService = Depends(Provide[SubtitleContainer.service]),
) -> Subtitle | JSONResponse:
    result = await service.get_subtitle_by_instance_id(instance_id)
    if result is None:
        # return None with 404 status code
        return JSONResponse(content=None, status_code=status.HTTP_404_NOT_FOUND)
    return result


@router.get(
    "/video/{video_instance_id}",
    response_model=list[Subtitle],
)
@inject
async def get_list_of_subtitles_by_video_instance_id(
    video_instance_id: int,
    service: SubtitleService = Depends(Provide[SubtitleContainer.service]),
) -> list[Subtitle]:
    result = await service.get_list_of_subtitles_by_video_instance_id(video_instance_id)
    return result


@router.get(
    "/",
    response_model=PaginatedResponse[Subtitle],
)
@inject
async def get_subtitles(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: SubtitleService = Depends(Provide[SubtitleContainer.service]),
) -> PaginatedResponse[Subtitle]:
    """
    Get paginated list of subtitles.

    - **page**: Page number (starting from 1)
    - **size**: Items per page (1-100, default 10)
    """
    return await service.get_paginated_subtitles(page, size)