from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class WorkerRegisterRequest(BaseModel):
    label: str
    machine_name: str
    gateway_url: str
    openclaw_mode: str = "openclaw"


class WorkerHeartbeatRequest(BaseModel):
    worker_id: UUID


class WorkerResponse(BaseModel):
    id: UUID
    label: str
    machine_name: str
    gateway_url: str
    status: str
    last_seen_at: Optional[datetime] = None
    openclaw_mode: str
    screen_stream_status: str
    created_at: datetime
