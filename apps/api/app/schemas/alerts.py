from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    CLEAR = "clear"
    INFORM = "inform"
    WATCH = "watch"
    WARNING = "warning"
    ACT_NOW = "act_now"


class AlertSource(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    timestamp: datetime
    official: bool = True


class NormalizedAlert(BaseModel):
    id: UUID
    raw_alert_id: Optional[str] = None
    headline: str
    location_label: str
    hazard_type: str
    severity: AlertSeverity
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    summary: str
    description: str
    instruction: Optional[str] = None
    recommended_actions: List[str] = Field(default_factory=list)
    source: AlertSource
    is_active: bool = True
    fetched_at: datetime
    geometry: Optional[Dict[str, Any]] = None


class RawAlert(BaseModel):
    id: UUID
    source_name: str
    external_id: str
    payload_json: Dict[str, Any]
    fetched_at: datetime
    processed: bool = False


class AlertSummaryResponse(BaseModel):
    """Lightweight projection for list views."""
    id: UUID
    headline: str
    location_label: str
    hazard_type: str
    severity: AlertSeverity
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    summary: str
    is_active: bool


class AlertDetailResponse(NormalizedAlert):
    pass
