"""
Tool: get_active_alerts

Returns the active alerts relevant to the user's monitored places,
filtered by optional minimum severity.
"""
from typing import Any, Dict, List

from app.schemas.alerts import AlertSeverity
from app.services import alert_matcher

_SEVERITY_ORDER = ["clear", "inform", "watch", "warning", "act_now"]


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    user_id: str = args["user_id"]
    severity_filter: str = args.get("severity_filter", "all")

    alerts = alert_matcher.alerts_for_user(user_id)

    if severity_filter != "all" and severity_filter in _SEVERITY_ORDER:
        min_index = _SEVERITY_ORDER.index(severity_filter)
        alerts = [
            a for a in alerts
            if _SEVERITY_ORDER.index(a.get("severity", "inform")) >= min_index
        ]

    if not alerts:
        return {
            "count": 0,
            "alerts": [],
            "summary": "No active alerts for your monitored locations.",
        }

    alert_list = [
        {
            "id": a["id"],
            "headline": a.get("headline", ""),
            "hazard_type": a.get("hazard_type", ""),
            "location": a.get("location_label", ""),
            "severity": a.get("severity", ""),
            "summary": a.get("summary", ""),
            "ends_at": a.get("ends_at"),
        }
        for a in alerts
    ]

    return {
        "count": len(alert_list),
        "alerts": alert_list,
        "summary": f"Found {len(alert_list)} active alert(s) for your area.",
    }
