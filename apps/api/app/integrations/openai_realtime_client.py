"""
OpenAI Realtime API client.

Mints ephemeral session tokens for the browser WebRTC connection.
The browser connects directly to OpenAI — the backend does not relay audio.

Docs: https://platform.openai.com/docs/guides/realtime-webrtc
"""
import logging
from pathlib import Path
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

REALTIME_SESSIONS_URL = "https://api.openai.com/v1/realtime/sessions"
DEFAULT_MODEL = "gpt-4o-realtime-preview-2024-12-17"
DEFAULT_VOICE = "alloy"

_PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "prompts"


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _build_instructions() -> str:
    system = _load_prompt("system_prompt.txt")
    safety = _load_prompt("safety_prompt.txt")
    escalation = _load_prompt("escalation_rules.txt")
    return f"{system}\n\n{safety}\n\n{escalation}"


async def create_ephemeral_session(
    tools: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
) -> Dict[str, Any]:
    """
    Create an OpenAI Realtime session and return the full response.
    The browser uses response['client_secret']['value'] for its WebRTC connection.
    """
    settings = get_settings()
    instructions = _build_instructions()

    payload: Dict[str, Any] = {
        "model": model,
        "voice": voice,
        "instructions": instructions,
        "tools": tools,
        "tool_choice": "auto",
        "input_audio_transcription": {"model": "whisper-1"},
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500,
        },
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

    logger.info("OpenAI Realtime session minted: %s", data.get("id"))
    return data
