"""
Tool: call_emergency_contact

Sends an SMS to an emergency contact via Twilio.
REQUIRES USER APPROVAL — external communication action.
"""
import logging
from typing import Any, Dict, Optional

from app.db.repositories import alert_repository, user_repository

logger = logging.getLogger(__name__)


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    contact_id: str = args["contact_id"]
    message: Optional[str] = args.get("message")
    alert_id: Optional[str] = args.get("alert_id")

    contact = user_repository.get_contact(contact_id)
    if not contact:
        return {"error": f"Contact {contact_id} not found."}

    alert_context = ""
    if alert_id:
        alert = alert_repository.get_alert(alert_id)
        if alert:
            alert_context = f" — {alert.get('headline', '')} ({alert.get('location_label', '')})"

    sms_body = message or f"Emergency alert{alert_context}. Please check in with me."

    try:
        from app.integrations.twilio_client import send_sms
        result = await send_sms(to=contact["phone"], body=sms_body)
        logger.info("SMS sent to contact %s", contact_id)
        return {
            "status": "sent",
            "contact_name": contact["name"],
            "phone": contact["phone"],
            "message": sms_body,
            "sid": result.get("sid"),
        }
    except Exception as exc:
        logger.error("SMS failed for contact %s: %s", contact_id, exc)
        return {
            "status": "error",
            "contact_name": contact.get("name", ""),
            "message": f"Could not send message: {exc}",
        }
