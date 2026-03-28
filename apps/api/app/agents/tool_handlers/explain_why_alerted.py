"""
Tool: explain_why_alerted

Explains in plain language why the user was alerted — which place was
affected and how the severity was determined.
"""
from typing import Any, Dict

from app.db.repositories import alert_repository, place_repository
from app.services.alert_classifier import EVENT_SEVERITY_OVERRIDES, NWS_SEVERITY_MAP


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    alert_id: str = args["alert_id"]
    user_id: str = args["user_id"]

    alert = alert_repository.get_alert(alert_id)
    if not alert:
        return {"error": f"Alert {alert_id} not found."}

    places = place_repository.list_for_user(user_id)
    place_labels = [p["label"] for p in places] if places else ["your monitored area"]

    hazard = alert.get("hazard_type", "Unknown hazard")
    severity = alert.get("severity", "unknown")
    location = alert.get("location_label", "your area")
    source = alert.get("source", {}).get("name", "official source")

    severity_reason = _severity_reason(hazard, severity)

    explanation = (
        f"You were alerted because a {hazard} is active in {location}, "
        f"which overlaps with {_format_places(place_labels)}. "
        f"The severity is '{severity}' {severity_reason}. "
        f"This alert comes from {source}, an official source."
    )

    return {
        "alert_id": alert_id,
        "hazard_type": hazard,
        "location": location,
        "severity": severity,
        "affected_places": place_labels,
        "explanation": explanation,
    }


def _format_places(labels: list) -> str:
    if not labels:
        return "your monitored area"
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f" and {labels[-1]}"


def _severity_reason(hazard: str, severity: str) -> str:
    if hazard in EVENT_SEVERITY_OVERRIDES:
        return f"because {hazard} events are classified as high-risk by default"
    reasons = {
        "act_now": "because an immediate threat to life has been identified",
        "warning": "because protective action is recommended",
        "watch": "because conditions are possible in the area",
        "inform": "as a general informational notice",
    }
    return reasons.get(severity, "")
