"""
Maps source-specific severity + event type → Haven internal severity tier.

Haven tiers (ascending):
  clear     – no active threat
  inform    – minor / informational
  watch     – potential threat, stay aware
  warning   – serious, take protective action
  act_now   – immediate life threat
"""
from app.schemas.alerts import AlertSeverity

_SEVERITY_ORDER = [
    AlertSeverity.CLEAR,
    AlertSeverity.INFORM,
    AlertSeverity.WATCH,
    AlertSeverity.WARNING,
    AlertSeverity.ACT_NOW,
]

NWS_SEVERITY_MAP: dict[str, AlertSeverity] = {
    "Extreme": AlertSeverity.ACT_NOW,
    "Severe": AlertSeverity.WARNING,
    "Moderate": AlertSeverity.WATCH,
    "Minor": AlertSeverity.INFORM,
    "Unknown": AlertSeverity.INFORM,
}

NWS_URGENCY_BOOST: dict[str, int] = {
    "Immediate": 1,
    "Expected": 0,
    "Future": -1,
    "Past": -2,
}

EVENT_SEVERITY_OVERRIDES: dict[str, AlertSeverity] = {
    # ACT NOW ─────────────────────────────────────────────────────────────────
    "Tornado Warning": AlertSeverity.ACT_NOW,
    "Flash Flood Emergency": AlertSeverity.ACT_NOW,
    "Extreme Wind Warning": AlertSeverity.ACT_NOW,
    "Tsunami Warning": AlertSeverity.ACT_NOW,
    "Shelter-In-Place Warning": AlertSeverity.ACT_NOW,
    "Evacuation - Immediate": AlertSeverity.ACT_NOW,
    "Radiological Hazard Warning": AlertSeverity.ACT_NOW,
    "Hazardous Materials Warning": AlertSeverity.ACT_NOW,
    # WARNING ──────────────────────────────────────────────────────────────────
    "Flash Flood Warning": AlertSeverity.WARNING,
    "Flood Warning": AlertSeverity.WARNING,
    "Severe Thunderstorm Warning": AlertSeverity.WARNING,
    "Winter Storm Warning": AlertSeverity.WARNING,
    "Blizzard Warning": AlertSeverity.WARNING,
    "Ice Storm Warning": AlertSeverity.WARNING,
    "Excessive Heat Warning": AlertSeverity.WARNING,
    "Red Flag Warning": AlertSeverity.WARNING,
    "Hurricane Warning": AlertSeverity.WARNING,
    "Tropical Storm Warning": AlertSeverity.WARNING,
    "High Wind Warning": AlertSeverity.WARNING,
    "Dust Storm Warning": AlertSeverity.WARNING,
    "Tsunami Advisory": AlertSeverity.WARNING,
    # WATCH ────────────────────────────────────────────────────────────────────
    "Flood Watch": AlertSeverity.WATCH,
    "Winter Storm Watch": AlertSeverity.WATCH,
    "Tornado Watch": AlertSeverity.WATCH,
    "Severe Thunderstorm Watch": AlertSeverity.WATCH,
    "Hurricane Watch": AlertSeverity.WATCH,
    "High Wind Watch": AlertSeverity.WATCH,
    "Excessive Heat Watch": AlertSeverity.WATCH,
    "Fire Weather Watch": AlertSeverity.WATCH,
    "Dense Fog Advisory": AlertSeverity.WATCH,
    # INFORM ───────────────────────────────────────────────────────────────────
    "Flood Advisory": AlertSeverity.INFORM,
    "Wind Advisory": AlertSeverity.INFORM,
    "Winter Weather Advisory": AlertSeverity.INFORM,
    "Frost Advisory": AlertSeverity.INFORM,
    "Heat Advisory": AlertSeverity.INFORM,
    "Air Quality Alert": AlertSeverity.INFORM,
    "Dense Smoke Advisory": AlertSeverity.INFORM,
    "Small Craft Advisory": AlertSeverity.INFORM,
}


def _tier_index(severity: AlertSeverity) -> int:
    return _SEVERITY_ORDER.index(severity)


def _clamp(index: int) -> AlertSeverity:
    return _SEVERITY_ORDER[max(1, min(index, len(_SEVERITY_ORDER) - 1))]


def classify_nws(nws_severity: str, nws_urgency: str, event_type: str) -> AlertSeverity:
    """Classify an NWS alert into a Haven severity tier."""
    if event_type in EVENT_SEVERITY_OVERRIDES:
        return EVENT_SEVERITY_OVERRIDES[event_type]

    base = NWS_SEVERITY_MAP.get(nws_severity, AlertSeverity.INFORM)
    boost = NWS_URGENCY_BOOST.get(nws_urgency, 0)
    return _clamp(_tier_index(base) + boost)


def classify_social(
    source_reliability: float,
    mention_count: int,
    corroborates_official: bool,
) -> AlertSeverity:
    """Social signals are capped at WATCH unless they confirm an official alert."""
    if corroborates_official:
        return AlertSeverity.WATCH
    if source_reliability >= 0.8 and mention_count >= 50:
        return AlertSeverity.WATCH
    if source_reliability >= 0.5 and mention_count >= 10:
        return AlertSeverity.INFORM
    return AlertSeverity.INFORM


def highest(severities: list[AlertSeverity]) -> AlertSeverity:
    """Return the highest severity from a collection."""
    if not severities:
        return AlertSeverity.CLEAR
    return max(severities, key=_tier_index)
