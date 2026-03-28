from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class CallContactRequest(BaseModel):
    contact_id: UUID
    alert_id: Optional[UUID] = None
    message: Optional[str] = None


class OpenGuidanceRequest(BaseModel):
    alert_id: UUID
    session_id: Optional[str] = None


class ApproveActionRequest(BaseModel):
    action_id: UUID
    reason: Optional[str] = None


class ActionLogResponse(BaseModel):
    id: UUID
    user_id: str
    action_type: str
    status: str
    payload_json: Optional[Dict[str, Any]] = None
    result_json: Optional[Dict[str, Any]] = None
    requires_approval: bool
    approved: Optional[bool] = None
