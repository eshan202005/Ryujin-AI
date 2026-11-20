from pydantic import BaseModel

class ChatRequest(BaseModel):
    message : str
    thread_id : str 
    include_status: bool = False

class ChatResponse(BaseModel):
    response: str
