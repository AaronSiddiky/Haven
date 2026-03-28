"""
Tool: update_monitoring_preferences

Updates the user's alert notification preferences in real time during a voice session.
"""
from typing import Any, Dict, Optional

from app.db.repositories import user_repository


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    user_id: str = args["user_id"]
    minimum_severity: Optional[str] = args.get("minimum_severity")
    voice_interruptions: Optional[bool] = args.get("voice_interruptions")

    updates: Dict[str, Any] = {}
    if minimum_severity:
        updates["minimum_severity"] = minimum_severity
    if voice_interruptions is not None:
        updates["voice_interruptions"] = voice_interruptions

    if not updates:
        return {"status": "no_change", "message": "No preferences to update."}

    user_repository.upsert_preferences(user_id, updates)

    confirmation_parts = []
    if minimum_severity:
        confirmation_parts.append(f"minimum alert level set to '{minimum_severity}'")
    if voice_interruptions is not None:
        state = "enabled" if voice_interruptions else "disabled"
        confirmation_parts.append(f"voice interruptions {state}")

    return {
        "status": "updated",
        "changes": updates,
        "message": f"Preferences updated: {', '.join(confirmation_parts)}.",
    }
