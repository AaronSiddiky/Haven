"""
Tool: read_official_guidance

Fetches and returns official guidance + recommended actions for a specific alert.
"""
from typing import Any, Dict

from app.db.repositories import alert_repository
from app.services import official_guidance_service


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    alert_id: str = args["alert_id"]

    alert = alert_repository.get_alert(alert_id)
    if not alert:
        return {"error": f"Alert {alert_id} not found."}

    guidance = official_guidance_service.guidance_for_alert(alert)

    return {
        "alert_id": alert_id,
        "headline": alert.get("headline", ""),
        "hazard_type": alert.get("hazard_type", ""),
        "location": alert.get("location_label", ""),
        "severity": alert.get("severity", ""),
        "instruction": guidance["instruction"],
        "recommended_actions": guidance["recommended_actions"],
        "guidance_url": guidance["guidance_url"],
        "source_url": guidance["source_url"],
    }
