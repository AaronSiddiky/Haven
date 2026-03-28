"""
Inline normalizer for the worker (avoids importing from apps/api).
Mirrors the logic in apps/api/app/services/alert_normalizer.py.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_SEVERITY_MAP = {
    "Extreme": "act_now", "Severe": "warning",
    "Moderate": "watch", "Minor": "inform", "Unknown": "inform",
}
_URGENCY_BOOST = {"Immediate": 1, "Expected": 0, "Future": -1, "Past": -2}
_ORDER = ["clear", "inform", "watch", "warning", "act_now"]

_EVENT_OVERRIDES = {
    "Tornado Warning": "act_now", "Flash Flood Emergency": "act_now",
    "Flash Flood Warning": "warning", "Flood Warning": "warning",
    "Severe Thunderstorm Warning": "warning", "Winter Storm Warning": "warning",
    "Tornado Watch": "watch", "Flood Watch": "watch",
    "Flood Advisory": "inform", "Wind Advisory": "inform",
}


def severity_from_nws(severity: str, urgency: str, event: str) -> str:
    if event in _EVENT_OVERRIDES:
        return _EVENT_OVERRIDES[event]
    base_idx = _ORDER.index(_SEVERITY_MAP.get(severity, "inform"))
    boost = _URGENCY_BOOST.get(urgency, 0)
    return _ORDER[max(1, min(base_idx + boost, len(_ORDER) - 1))]


def normalize_nws_feature(feature: Dict[str, Any], raw_id: str) -> Dict[str, Any]:
    props = feature.get("properties", {})
    severity = severity_from_nws(
        props.get("severity", "Unknown"),
        props.get("urgency", "Unknown"),
        props.get("event", ""),
    )
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": str(uuid.uuid4()),
        "raw_alert_id": raw_id,
        "headline": props.get("headline") or props.get("event", "Alert"),
        "location_label": props.get("areaDesc", "Unknown area"),
        "hazard_type": props.get("event", "Unknown"),
        "severity": severity,
        "starts_at": props.get("onset") or props.get("effective"),
        "ends_at": props.get("expires") or props.get("ends"),
        "summary": f"{props.get('event', 'Alert')} in {props.get('areaDesc', 'your area')}.",
        "description": props.get("description", ""),
        "instruction": props.get("instruction"),
        "recommended_actions": [],
        "source": {
            "id": props.get("id") or props.get("@id", ""),
            "name": "NWS",
            "url": props.get("@id"),
            "timestamp": now,
            "official": True,
        },
        "is_active": True,
        "fetched_at": now,
        "geometry": feature.get("geometry"),
    }
