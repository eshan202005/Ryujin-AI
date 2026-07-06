from fastapi import FastAPI

from backend.routers.root import router as root_router
from backend.routers.chat import router as chat_router


app = FastAPI(
    title="Ryujin AI",
    version="0.1.0",
)

app.include_router(root_router,tags=["Root"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
