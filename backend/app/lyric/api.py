from .container import LyricContainer
from .service import LyricService
from .dto import AddLyric, Lyric, PaginatedResponse

from fastapi.routing import APIRouter
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/lyric", tags=["lyric"])


@router.post("/", response_model=Lyric, responses={404: {"description": "Not found"}})
@inject
async def add_lyric(
    dto: AddLyric,
    service: LyricService = Depends(Provide[LyricContainer.service]),
) -> Lyric | JSONResponse:
    try:
        return await service.add_lyric(dto)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{instance_id}",
    response_model=Lyric,
    responses={404: {"description": "Not found"}},
)
@inject
async def get_lyric_by_instance_id(
    instance_id: int,
    service: LyricService = Depends(Provide[LyricContainer.service]),
) -> Lyric | JSONResponse:
    result = await service.get_lyric_by_instance_id(instance_id)
    if result is None:
        # return None with 404 status code
        return JSONResponse(content=None, status_code=status.HTTP_404_NOT_FOUND)
    return result


@router.get(
    "/video/{video_instance_id}",
    response_model=list[Lyric],
)
@inject
async def get_list_of_lyrics_by_video_instance_id(
    video_instance_id: int,
    service: LyricService = Depends(Provide[LyricContainer.service]),
) -> list[Lyric]:
    result = await service.get_list_of_lyrics_by_video_instance_id(video_instance_id)
    return result


@router.get(
    "/",
    response_model=PaginatedResponse[Lyric],
)
@inject
async def get_lyrics(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: LyricService = Depends(Provide[LyricContainer.service]),
) -> PaginatedResponse[Lyric]:
    """
    Get paginated list of lyrics.

    - **page**: Page number (starting from 1)
    - **size**: Items per page (1-100, default 10)
    """
    return await service.get_paginated_lyrics(page, size)
