from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class OpenClawExecuteRequest(BaseModel):
    session_id: UUID
    tool_name: str
    params: Dict[str, Any] = {}


class OpenClawCancelRequest(BaseModel):
    run_id: str


class ActionLogResponse(BaseModel):
    id: UUID
    session_id: UUID
    tool_name: str
    status: str
    message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
