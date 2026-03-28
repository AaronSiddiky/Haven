from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.alerts import AlertSeverity


class PreferencesUpdate(BaseModel):
    minimum_severity: Optional[AlertSeverity] = None
    voice_interruptions: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    hazard_types_filter: Optional[List[str]] = None


class PreferencesResponse(BaseModel):
    id: UUID
    user_id: str
    minimum_severity: AlertSeverity
    voice_interruptions: bool
    sms_notifications: bool
    hazard_types_filter: List[str]
