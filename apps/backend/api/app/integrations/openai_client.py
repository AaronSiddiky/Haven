"""
OpenAI integration helpers.

Realtime ephemeral-token minting uses a direct HTTP call because
the official Python SDK does not yet expose the /v1/realtime/sessions endpoint.
"""
import logging
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

REALTIME_SESSIONS_URL = "https://api.openai.com/v1/realtime/sessions"
DEFAULT_MODEL = "gpt-4o-realtime-preview-2024-12-17"
DEFAULT_VOICE = "alloy"


async def create_realtime_session(
    instructions: str,
    tools: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
) -> Dict[str, Any]:
    """
    Mint an ephemeral session for the browser WebRTC client.

    Returns the full session object; the browser needs:
        response["client_secret"]["value"]
    """
    settings = get_settings()
    payload: Dict[str, Any] = {
        "model": model,
        "voice": voice,
        "instructions": instructions,
        "tools": tools,
        "tool_choice": "auto",
        "input_audio_transcription": {"model": "whisper-1"},
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            REALTIME_SESSIONS_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info("OpenAI Realtime session created: %s", data.get("id"))
        return data
