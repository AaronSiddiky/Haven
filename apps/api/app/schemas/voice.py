from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class VoiceSessionRequest(BaseModel):
    user_id: str


class VoiceSessionResponse(BaseModel):
    session_id: str
    client_secret: str
    model: str
    expires_at: Optional[str] = None


class TranscriptTurn(BaseModel):
    speaker: str
    text: str
    timestamp: Optional[str] = None


class ToolCallEvent(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str
