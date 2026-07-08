from fastapi import APIRouter
from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import chat

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    response = await chat(request.message)

    return ChatResponse(
        response=response
    )