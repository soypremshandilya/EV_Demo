"""POST /chat — send a user message to Gemini and return the response."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gemini import chat

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        reply = chat(req.message, req.history)
        return ChatResponse(reply=reply)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini error: {str(e)}")
