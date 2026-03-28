"""
Voice session routes.

POST /voice/session  → mint OpenAI Realtime ephemeral token for browser WebRTC
POST /voice/tool-result → receive tool call result from the browser (for server-side dispatch)
"""
import uuid
from fastapi import APIRouter, Header, HTTPException
from typing import Any, Dict

from app.agents import tool_registry
from app.agents.session_manager import session_manager
from app.integrations.openai_realtime_client import create_ephemeral_session
from app.schemas.voice import VoiceSessionRequest

router = APIRouter()


@router.post("/session")
async def create_voice_session(body: VoiceSessionRequest):
    """
    Mint an ephemeral OpenAI Realtime token.
    The browser uses client_secret.value to connect via WebRTC directly to OpenAI.
    """
    try:
        result = await create_ephemeral_session(tools=tool_registry.TOOLS)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI Realtime error: {exc}")

    session_id = result.get("id", str(uuid.uuid4()))
    session_manager.create(session_id, body.user_id)

    return {
        "session_id": session_id,
        "client_secret": result.get("client_secret", {}).get("value"),
        "model": result.get("model"),
        "expires_at": result.get("client_secret", {}).get("expires_at"),
    }


@router.post("/tool-result")
async def handle_tool_call(body: Dict[str, Any]):
    """
    Dispatch a tool call from the browser's data channel to the correct handler.
    Returns the tool result so the browser can send it back to OpenAI.
    """
    tool_name: str = body.get("tool_name", "")
    arguments: Dict[str, Any] = body.get("arguments", {})
    call_id: str = body.get("call_id", "")

    if not tool_name:
        raise HTTPException(status_code=400, detail="tool_name is required")

    try:
        result = await tool_registry.dispatch(tool_name, arguments)
    except Exception as exc:
        result = {"error": str(exc)}

    return {"call_id": call_id, "tool_name": tool_name, "result": result}
