from fastapi import APIRouter

from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import chat , stream_chat

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    response = await chat(
        request.message,
        request.thread_id,
    )

    return ChatResponse(
        response=response
    )
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def stream_chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        stream_chat(
            request.message,
            request.thread_id,
        ),
        media_type="text/plain",
    )