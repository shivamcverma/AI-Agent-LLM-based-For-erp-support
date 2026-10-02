from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import ChatService


router = APIRouter()

chat_service = ChatService()


class ChatRequest(BaseModel):
    message: str
    school_id: int
    conversation_history: list[dict] = []
    previous_understanding: dict | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    result = await chat_service.process_message(
        message=request.message,
        school_id=request.school_id,
        conversation_history=request.conversation_history,
        previous_understanding=request.previous_understanding
    )
    return result