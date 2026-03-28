from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: UUID
    session_id: UUID
    action_type: str
    payload_json: Dict[str, Any]
    status: str
    requested_at: datetime
    resolved_at: Optional[datetime] = None


class ApprovalResolveRequest(BaseModel):
    reason: Optional[str] = None
