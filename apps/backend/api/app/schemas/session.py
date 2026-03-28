from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SessionCreate(BaseModel):
    pass


class AttachWorkerRequest(BaseModel):
    worker_id: UUID


class SessionResponse(BaseModel):
    id: UUID
    status: str
    livekit_room_name: str
    openai_session_id: Optional[str] = None
    worker_id: Optional[UUID] = None
    created_at: datetime
    ended_at: Optional[datetime] = None
