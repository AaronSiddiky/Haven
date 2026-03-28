"""
OpenAI Realtime session management.

Mints ephemeral tokens for browser WebRTC connections.
The browser uses client_secret.value to connect directly to OpenAI.
"""
import logging
from typing import Any, Dict, List

from app.integrations.openai_client import create_realtime_session
from app.services import session_service

logger = logging.getLogger(__name__)

HAVEN_INSTRUCTIONS = """
You are Haven, a voice-first assistant that helps users by controlling a remote browser.
You have access to tools that perform browser automation on the user's behalf.

Rules:
- Always confirm before taking irreversible actions (purchases, bookings, sending messages).
- Narrate what you are doing in simple, clear language.
- If unsure, ask the user before proceeding.
- Keep responses concise – the user can see the browser moving in real time.
"""

HAVEN_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "name": "open_official_guidance",
        "description": "Open an official government or authority guidance page on the remote browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look up"},
                "session_id": {"type": "string", "description": "Current Haven session ID"},
            },
            "required": ["query", "session_id"],
        },
    },
    {
        "type": "function",
        "name": "search_transport_options",
        "description": "Search for transport options (flights, trains, buses) on the remote browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "date": {"type": "string"},
                "session_id": {"type": "string"},
            },
            "required": ["origin", "destination", "session_id"],
        },
    },
    {
        "type": "function",
        "name": "compare_sources",
        "description": "Open and compare multiple official sources on the remote browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "session_id": {"type": "string"},
            },
            "required": ["topic", "session_id"],
        },
    },
    {
        "type": "function",
        "name": "prepare_call_contact",
        "description": "Find contact information and prepare to place a call or send a message. Requires approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "contact_type": {"type": "string", "description": "e.g. airline, embassy, emergency services"},
                "context": {"type": "string"},
                "session_id": {"type": "string"},
            },
            "required": ["contact_type", "session_id"],
        },
    },
]


async def mint_ephemeral_token(session_id: str) -> dict:
    """
    Create an OpenAI Realtime session and persist the session ID.
    Returns the full session object including client_secret.
    """
    result = await create_realtime_session(
        instructions=HAVEN_INSTRUCTIONS,
        tools=HAVEN_TOOLS,
    )
    openai_session_id = result.get("id", "")
    if openai_session_id and session_id:
        session_service.set_openai_session(session_id, openai_session_id)
    logger.info("Ephemeral token minted for Haven session %s", session_id)
    return result
