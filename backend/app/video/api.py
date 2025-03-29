from .container import VideoContainer
from .service import VideoService
from .dto import RetrievalVideo, Video

from fastapi.routing import APIRouter
from fastapi import Depends
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/video", tags=["videos"])


@router.post("/retrieval")
@inject
async def retrieval(
    dto: RetrievalVideo,
    service: VideoService = Depends(Provide[VideoContainer.service]),
) -> Video:
    return await service.retrieval_video(dto)
