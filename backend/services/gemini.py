"""
Gemini service — wraps Google Gemini 2.5 Flash with function-calling tools.

Workflow:
  1. User message + history → Gemini (with tool declarations)
  2. If Gemini returns a function_call → execute the matching db_tool → feed result back
  3. Repeat until Gemini returns a text response
  4. Return the final text to the caller

The LLM never generates SQL. SQL lives only inside tools/db_tools.py.
"""

import json
import os
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

SYSTEM_PROMPT = (
    "You are VoltRide AI, an internal assistant for an EV scooter subscription company. "
    "The company rents scooters hourly, daily, or monthly. Scooters use swappable batteries. "
    "You help employees look up operational information. "
    "You are READ ONLY — you never modify any data. "
    "You have access to database tools that fetch live data. Use them to answer questions accurately. "
    "NEVER generate or mention SQL queries — just call the appropriate tool. "
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
            if fn is None:
                result = {"error": f"Unknown tool: {fc.name}"}
            else:
                try:
                    result = fn(**fc.args) if fc.args else fn()
                except Exception as e:
                    result = {"error": str(e)}

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

    return response.text or "I wasn't able to generate a response. Please try again."
