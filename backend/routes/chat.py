"""POST /chat — send a user message to Gemini and return the response.

Conversation history is stored server-side, keyed by session_id.

Security layers (read-only enforcement):
  1. Route-level:  regex blocks messages containing INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE
  2. Prompt-level: system prompt instructs Gemini to refuse modification requests
  3. Tool-level:   db_tools.py only exposes SELECT queries — no write functions exist

Permitted AI capabilities:
  ✓ Retrieve   — call read-only database tools to fetch live data
  ✓ Analyze    — compare, compute stats, and identify trends from results
  ✓ Summarize  — condense data and company documents into concise answers
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

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_TURNS = 50  # per session — prevent unbounded memory growth


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # ── Input validation ──
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if len(req.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters.",
        )

    # Resolve or create session
    session_id = req.session_id or str(uuid.uuid4())
    history = _sessions[session_id]

    # Trim old history if it gets too long (keep most recent turns)
    if len(history) > MAX_HISTORY_TURNS * 2:
        _sessions[session_id] = history[-MAX_HISTORY_TURNS * 2 :]
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
        # Config errors (missing API key, etc.)
        raise HTTPException(status_code=500, detail=str(e))
    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The AI service took too long to respond. Please try again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable. Please try again later.",
        )

    # Guard against None/empty replies
    if not reply or not reply.strip():
        reply = "I wasn't able to generate a response. Please try rephrasing your question."

    # Persist this turn in the session
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    return ChatResponse(reply=reply, session_id=session_id)
