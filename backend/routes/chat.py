"""POST /chat — send a user message to Gemini and return the response.

Conversation history is stored server-side, keyed by session_id.
"""

import re
import uuid
from collections import defaultdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gemini import chat

router = APIRouter(tags=["Chat"])

READONLY_REFUSAL = "I only have permission to retrieve and analyze information."

# Dangerous SQL keywords that indicate a data-modification intent
_BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b", re.IGNORECASE
)

# ── In-memory session store ──
# { session_id: [ { "role": "user"|"assistant", "content": "..." }, ... ] }
_sessions: dict[str, list[dict]] = defaultdict(list)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Resolve or create session
    session_id = req.session_id or str(uuid.uuid4())
    history = _sessions[session_id]

    # Block any message containing data-modification SQL keywords
    if _BLOCKED_KEYWORDS.search(req.message):
        # Still record the exchange so history stays coherent
        history.append({"role": "user", "content": req.message})
        history.append({"role": "assistant", "content": READONLY_REFUSAL})
        return ChatResponse(reply=READONLY_REFUSAL, session_id=session_id)

    try:
        reply = chat(req.message, history)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini error: {str(e)}")

    # Persist this turn in the session
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    return ChatResponse(reply=reply, session_id=session_id)
