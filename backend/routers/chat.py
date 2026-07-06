from fastapi import APIRouter
from backend.models import ChatRequest, ChatResponse


router = APIRouter()

@router.post("/",response_model=ChatResponse)
async def chat(request: ChatRequest):
    return ChatResponse(
        response=f"You said: {request.message}"
    )