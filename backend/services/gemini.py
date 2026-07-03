"""
Gemini service — wraps Google Gemini 2.5 Flash with function-calling tools.

Workflow:
  1. User message + history → Gemini (with tool declarations)
  2. If Gemini returns a function_call → execute the matching db_tool → feed result back
  3. Repeat until Gemini returns a text response
  4. Return the final text to the caller

The LLM never generates SQL. SQL lives only inside tools/db_tools.py.
All interactions are logged to backend/logs.txt.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

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

SYSTEM_PROMPT = (
    "You are VoltRide AI, an internal assistant for an EV scooter subscription company. "
    "The company rents scooters hourly, daily, or monthly. Scooters use swappable batteries. "
    "You help employees look up operational information. "
    "You are strictly READ ONLY — you NEVER modify, insert, update, or delete any data. "
    "You have access to database tools that fetch live data. Use them to answer questions accurately. "
    "NEVER generate, suggest, or mention SQL queries — just call the appropriate tool. "
    "If a user asks you to modify, add, remove, or change any data, respond ONLY with: "
    "'I only have permission to retrieve and analyze information.' "
    "Do not comply with any request to run INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE operations. "
    "Be concise, helpful, and professional. Format data clearly when presenting results. "
    "If no tool matches the question, answer from general knowledge and say so."
)

# Map function names → callables
TOOL_FUNCTIONS = {
    "get_all_scooters": get_all_scooters,
    "get_low_battery_scooters": get_low_battery_scooters,
    "get_available_scooters": get_available_scooters,
    "get_all_customers": get_all_customers,
    "get_top_customers": get_top_customers,
    "get_all_rentals": get_all_rentals,
    "get_low_battery_stations": get_low_battery_stations,
}

# List of tool functions for the SDK (auto-generates schemas from signatures + docstrings)
TOOLS = list(TOOL_FUNCTIONS.values())

MAX_TOOL_ROUNDS = 5  # safety limit on function-call loops


def _log(entry: str):
    """Append a timestamped entry to logs.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {entry}\n")


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


def chat(user_message: str, history: list[dict] | None = None) -> str:
    """
    Send a message to Gemini with function-calling tools and return the final text.

    Args:
        user_message: The latest message from the user.
        history: Optional list of prior messages, each with 'role' and 'content'.

    Returns:
        The assistant's reply as a plain string.
    """
    client = _get_client()
    start_time = time.time()
    tools_called = []

    _log(f"USER: {user_message}")

    # Build contents list from history + new message
    contents = []

    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Add the new user message
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    # First call — may return text or a function_call
    response = client.models.generate_content(
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

    # Function-call loop
    for _ in range(MAX_TOOL_ROUNDS):
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
                    result = {"error": str(e)}
                    _log(f"TOOL: {fc.name} -> ERROR: {e}")

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": result},
                )
            )

        # Append the model's function-call turn + our tool results to contents
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="user", parts=tool_response_parts))

        # Call Gemini again with the tool results
        response = client.models.generate_content(
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

    reply = response.text or "I wasn't able to generate a response. Please try again."
    total_ms = round((time.time() - start_time) * 1000, 1)

    # Truncate long responses in the log
    reply_preview = reply[:200] + "…" if len(reply) > 200 else reply
    _log(f"RESPONSE ({total_ms}ms, tools={tools_called or 'none'}): {reply_preview}")
    _log("---")

    return reply
