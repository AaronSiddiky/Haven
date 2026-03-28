"""
Converts raw source payloads (NWS CAP, etc.) into the internal NormalizedAlert schema.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.schemas.alerts import AlertSource, AlertSeverity, NormalizedAlert
from app.services.alert_classifier import classify_nws

NWS_SOURCE_NAME = "NWS"


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _recommended_actions(response: str, instruction: Optional[str]) -> List[str]:
    """Generate human-readable recommended actions from NWS response codes."""
    action_map = {
        "Evacuate": "Evacuate the area immediately",
        "Shelter": "Shelter in place",
        "Prepare": "Prepare an emergency kit",
        "Execute": "Follow official instructions immediately",
        "Avoid": "Avoid the affected area",
        "Monitor": "Monitor official updates",
        "AllClear": "All clear — normal activities may resume",
        "None": "Monitor the situation",
    }
    actions = []
    if response and response in action_map:
        actions.append(action_map[response])
    if instruction:
        actions.append("Follow official instructions")
    if not actions:
        actions.append("Monitor official sources for updates")
    return actions


def from_nws_feature(feature: Dict[str, Any], raw_alert_id: Optional[str] = None) -> NormalizedAlert:
    """Convert a single NWS GeoJSON Feature into a NormalizedAlert."""
    props = feature.get("properties", {})

    severity = classify_nws(
        nws_severity=props.get("severity", "Unknown"),
        nws_urgency=props.get("urgency", "Unknown"),
        event_type=props.get("event", ""),
    )

    external_id = props.get("id") or props.get("@id") or feature.get("id", "")
    headline = props.get("headline") or props.get("event", "Alert")
    area_desc = props.get("areaDesc", "Unknown area")
    description = props.get("description", "")
    instruction = props.get("instruction")
    response = props.get("response", "Monitor")

    sent_str = props.get("sent") or props.get("effective")
    onset_str = props.get("onset")
    expires_str = props.get("expires") or props.get("ends")

    source = AlertSource(
        id=external_id,
        name=NWS_SOURCE_NAME,
        url=props.get("@id"),
        timestamp=_parse_dt(sent_str) or datetime.now(timezone.utc),
        official=True,
    )

    summary = _build_summary(props.get("event", "Alert"), area_desc, severity)

    return NormalizedAlert(
        id=uuid.uuid4(),
        raw_alert_id=raw_alert_id,
        headline=headline,
        location_label=area_desc,
        hazard_type=props.get("event", "Unknown"),
        severity=severity,
        starts_at=_parse_dt(onset_str or sent_str),
        ends_at=_parse_dt(expires_str),
        summary=summary,
        description=description,
        instruction=instruction,
        recommended_actions=_recommended_actions(response, instruction),
        source=source,
        is_active=True,
        fetched_at=datetime.now(timezone.utc),
        geometry=feature.get("geometry"),
    )


def _build_summary(event_type: str, area: str, severity: AlertSeverity) -> str:
    tier_labels = {
        AlertSeverity.ACT_NOW: "Take immediate action",
        AlertSeverity.WARNING: "Protective action recommended",
        AlertSeverity.WATCH: "Conditions possible — stay alert",
        AlertSeverity.INFORM: "Informational notice",
        AlertSeverity.CLEAR: "No active threat",
    }
    label = tier_labels.get(severity, "")
    return f"{event_type} in {area}. {label}."
