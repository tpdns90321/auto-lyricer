from .container import TranscriptionContainer
from .service import TranscriptionService
from .dto import CreateTranscription, Transcription, PaginatedResponse

from fastapi.routing import APIRouter
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/transcription", tags=["transcription"])


@router.post(
    "/", response_model=Transcription, responses={404: {"description": "Not found"}}
)
@inject
async def create_transcription(
    dto: CreateTranscription,
    service: TranscriptionService = Depends(Provide[TranscriptionContainer.service]),
) -> Transcription | JSONResponse:
    try:
        return await service.create_transcription(dto)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{instance_id}",
    response_model=Transcription,
    responses={404: {"description": "Not found"}},
)
@inject
async def get_transcription_by_instance_id(
    instance_id: int,
    service: TranscriptionService = Depends(Provide[TranscriptionContainer.service]),
) -> Transcription | JSONResponse:
    result = await service.get_transcription_by_instance_id(instance_id)
    if result is None:
        # return None with 404 status code
        return JSONResponse(content=None, status_code=status.HTTP_404_NOT_FOUND)
    return result


@router.get(
    "/",
    response_model=PaginatedResponse[Transcription],
)
@inject
async def get_transcriptions(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    video_instance_id: int | None = Query(
        None, description="Filter by video instance ID"
    ),
    service: TranscriptionService = Depends(Provide[TranscriptionContainer.service]),
) -> PaginatedResponse[Transcription]:
    """Get paginated list of transcriptions.

    - **page**: Page number (starting from 1)
    - **size**: Items per page (1-100, default 10)
    - **video_instance_id**: Optional filter by video instance ID
    """
    return await service.get_paginated_transcriptions(page, size, video_instance_id)
