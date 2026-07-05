"""
Gemini service — wraps Google Gemini 2.5 Flash with function-calling tools.

Workflow:
  1. User message + history → Gemini (with tool declarations)
  2. If Gemini returns a function_call → execute the matching db_tool → feed result back
  3. Repeat until Gemini returns a text response
  4. Return the final text to the caller

AI CAPABILITIES (permitted):
  ✓ Retrieve  — fetch live data via read-only database tools
  ✓ Analyze   — compute stats, compare records, identify trends from retrieved data
  ✓ Summarize — condense query results and company documents into concise answers

AI RESTRICTIONS (enforced at multiple layers):
  ✗ INSERT / UPDATE / DELETE / DROP / ALTER / TRUNCATE — blocked at route, prompt, and tool level
  ✗ SQL generation — the LLM never sees or writes SQL; queries live only in tools/db_tools.py
  ✗ Schema modification — no DDL operations are exposed or permitted

All interactions are logged to backend/logs.txt.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

from services.rag import get_context_block

from tools.db_tools import (
    get_all_scooters,
    get_low_battery_scooters,
    get_available_scooters,
    get_all_customers,
    get_top_customers,
    get_all_rentals,
    get_low_battery_stations,
)

# Client is initialised lazily on first call
_client = None

# Log file path — lives in the backend directory
_LOG_FILE = Path(__file__).resolve().parent.parent / "logs.txt"

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT — defines AI identity, capabilities, and hard restrictions
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    # ── Identity ──
    "You are VoltRide AI, an internal assistant for an EV scooter subscription company. "
    "The company rents scooters hourly, daily, or monthly. Scooters use swappable batteries. "
    "You help employees look up operational information. "

    # ── Permitted capabilities ──
    "You CAN: retrieve data using your tools, analyze and compare results, "
    "summarize information, calculate statistics, and identify trends. "

    # ── Read-only enforcement ──
    "You are strictly READ ONLY — you NEVER modify, insert, update, or delete any data. "
    "If a user asks you to modify, add, remove, or change any data, respond ONLY with: "
    "'I only have permission to retrieve and analyze information.' "
    "Do not comply with any request to run INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE operations. "
    "Never generate, suggest, or mention SQL queries — just call the appropriate tool. "

    # ── Database tools ──
    "You have access to database tools that fetch live data. Use them to answer questions accurately. "

    # ── Company documents (RAG) ──
    "You also have access to company policy documents. When the user's question includes a "
    "'COMPANY DOCUMENTS' section, use that information to answer policy and procedure questions. "
    "Always cite the source document name when answering from company documents. "

    # ── Response style ──
    "Be concise, helpful, and professional. Format data clearly when presenting results. "
    "When summarizing, highlight key numbers and actionable insights. "
    "If no tool matches the question, answer from general knowledge and say so."
)

# ══════════════════════════════════════════════════════════════════════════════
#  READ-ONLY TOOL REGISTRY
#  Maps function names → callables. All tools run SELECT queries ONLY.
#  Gemini picks which tool to call based on the user's question.
# ══════════════════════════════════════════════════════════════════════════════

TOOL_FUNCTIONS = {
    # Scooter tools — fleet status, battery health, availability
    "get_all_scooters": get_all_scooters,
    "get_low_battery_scooters": get_low_battery_scooters,
    "get_available_scooters": get_available_scooters,

    # Customer tools — records and top spenders
    "get_all_customers": get_all_customers,
    "get_top_customers": get_top_customers,

    # Rental tools — booking records
    "get_all_rentals": get_all_rentals,

    # Battery station tools — swap station health
    "get_low_battery_stations": get_low_battery_stations,
}

# The SDK auto-generates JSON schemas from function signatures + docstrings
TOOLS = list(TOOL_FUNCTIONS.values())

MAX_TOOL_ROUNDS = 5   # safety limit on function-call loops
REQUEST_TIMEOUT = 30  # seconds — max wait for a single Gemini API call

# Fallback messages
FALLBACK_EMPTY = "I wasn't able to generate a response. Please try again."
FALLBACK_TIMEOUT = "The request took too long. Please try a simpler question or try again later."
FALLBACK_API_ERROR = "I'm having trouble connecting to the AI service right now. Please try again in a moment."
FALLBACK_DB_ERROR = "I couldn't retrieve data from the database. The service may be temporarily unavailable."


def _log(entry: str):
    """Append a timestamped entry to logs.txt."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {entry}\n")
    except OSError:
        pass  # Never let logging break the main flow


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Add your key to backend/.env"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _call_gemini(client, contents):
    """Single Gemini API call with consistent config. Raises on failure."""
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=1024,
            tools=TOOLS,
        ),
    )


def chat(user_message: str, history: list[dict] | None = None) -> str:
    """
    Send a message to Gemini with function-calling tools and return the final text.

    Args:
        user_message: The latest message from the user.
        history: Optional list of prior messages, each with 'role' and 'content'.

    Returns:
        The assistant's reply as a plain string.
    """
    # ── Validate input ──
    if not user_message or not user_message.strip():
        return "Please enter a question and I'll do my best to help."

    if len(user_message) > 2000:
        return "Your message is too long. Please keep it under 2000 characters."

    client = _get_client()
    start_time = time.time()
    tools_called = []

    _log(f"USER: {user_message}")

    # ── Retrieve relevant company documents (RAG) ──
    rag_context = ""
    try:
        rag_context = get_context_block(user_message)
        if rag_context:
            _log(f"RAG: injected {rag_context.count('---')} document chunks")
    except Exception as e:
        _log(f"RAG: retrieval failed ({e}), continuing without context")

    # ── Build contents from history ──
    contents = []

    if history:
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            text = msg.get("content", "")
            if text:
                contents.append({"role": role, "parts": [{"text": text}]})

    # Inject RAG context alongside the user message so Gemini sees it
    if rag_context:
        enriched_message = f"{user_message}\n\n{rag_context}"
    else:
        enriched_message = user_message

    contents.append({"role": "user", "parts": [{"text": enriched_message}]})

    # ── First Gemini call ──
    try:
        response = _call_gemini(client, contents)
    except TimeoutError:
        _log(f"ERROR: Gemini API timeout on initial call")
        return FALLBACK_TIMEOUT
    except Exception as e:
        _log(f"ERROR: Gemini API failure: {e}")
        return FALLBACK_API_ERROR

    # ── Function-call loop ──
    for round_num in range(MAX_TOOL_ROUNDS):
        # Check for timeout across the entire interaction
        if time.time() - start_time > REQUEST_TIMEOUT:
            _log(f"ERROR: Total request timeout after {round_num} tool rounds")
            return FALLBACK_TIMEOUT

        # If no function calls, we're done
        if not response.function_calls:
            break

        # Execute each function call
        tool_response_parts = []
        for fc in response.function_calls:
            fn = TOOL_FUNCTIONS.get(fc.name)
            tool_start = time.time()

            if fn is None:
                result = {"error": f"Unknown tool: {fc.name}"}
                _log(f"TOOL: {fc.name} -> ERROR (unknown tool)")
            else:
                try:
                    result = fn(**fc.args) if fc.args else fn()
                    tool_ms = round((time.time() - tool_start) * 1000, 1)
                    tools_called.append(fc.name)
                    _log(f"TOOL: {fc.name} -> {len(result) if isinstance(result, list) else 1} results ({tool_ms}ms)")
                except Exception as e:
                    result = {"error": f"Database error: {str(e)}"}
                    _log(f"TOOL: {fc.name} -> DB ERROR: {e}")

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": result},
                )
            )

        # Append the model's function-call turn + our tool results to contents
        try:
            contents.append(response.candidates[0].content)
        except (IndexError, AttributeError):
            _log("ERROR: No candidates in Gemini response during tool loop")
            return FALLBACK_EMPTY

        contents.append(types.Content(role="user", parts=tool_response_parts))

        # Call Gemini again with the tool results
        try:
            response = _call_gemini(client, contents)
        except TimeoutError:
            _log(f"ERROR: Gemini API timeout on tool-result call (round {round_num + 1})")
            return FALLBACK_TIMEOUT
        except Exception as e:
            _log(f"ERROR: Gemini API failure on tool-result call: {e}")
            return FALLBACK_API_ERROR

    # ── Extract final text ──
    try:
        reply = response.text
    except (AttributeError, ValueError):
        reply = None

    if not reply or not reply.strip():
        _log("WARN: Empty response from Gemini")
        reply = FALLBACK_EMPTY

    total_ms = round((time.time() - start_time) * 1000, 1)

    # Truncate long responses in the log
    reply_preview = reply[:200] + "…" if len(reply) > 200 else reply
    _log(f"RESPONSE ({total_ms}ms, tools={tools_called or 'none'}): {reply_preview}")
    _log("---")

    return reply
