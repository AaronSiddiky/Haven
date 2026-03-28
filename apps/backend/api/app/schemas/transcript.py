from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TranscriptTurnCreate(BaseModel):
    session_id: UUID
    speaker: str
    text: str


class TranscriptTurnResponse(BaseModel):
    id: UUID
    session_id: UUID
    speaker: str
    text: str
    timestamp: datetime
