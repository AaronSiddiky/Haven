"""
Job: notify_users

For each user with sms_notifications=True, send an SMS for any new
warning/act_now alerts that match their monitored places and haven't
been notified yet.
"""
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from supabase import create_client

from src.settings import get_settings

logger = logging.getLogger(__name__)

_HIGH_SEVERITY = {"warning", "act_now"}
_NOTIFY_WINDOW_MINUTES = 6


async def run() -> None:
    settings = get_settings()
    if not settings.twilio_account_sid:
        logger.debug("Twilio not configured — skipping notifications")
        return

    db = create_client(settings.supabase_url, settings.supabase_service_key)

    window_start = (datetime.now(timezone.utc) - timedelta(minutes=_NOTIFY_WINDOW_MINUTES)).isoformat()
    new_alerts = (
        db.table("normalized_alerts")
        .select("*")
        .eq("is_active", True)
        .in_("severity", list(_HIGH_SEVERITY))
        .gte("fetched_at", window_start)
        .execute()
    ).data

    if not new_alerts:
        return

    users_with_sms = (
        db.table("user_preferences").select("user_id").eq("sms_notifications", True).execute()
    ).data

    for user_pref in users_with_sms:
        user_id = user_pref["user_id"]
        contacts = (
            db.table("emergency_contacts")
            .select("phone, name")
            .eq("user_id", user_id)
            .eq("notify_automatically", True)
            .execute()
        ).data

        places = (
            db.table("monitored_places").select("*").eq("user_id", user_id).execute()
        ).data

        for alert in new_alerts:
            if not _alert_relevant(alert, places):
                continue
            for contact in contacts:
                await _send_notification(settings, contact, alert)


def _alert_relevant(alert: Dict[str, Any], places: List[Dict[str, Any]]) -> bool:
    if not places:
        return True
    geometry = alert.get("geometry")
    if not geometry:
        return True
    for place in places:
        dist = _haversine(place.get("lat", 0), place.get("lon", 0), 0, 0)
        if dist <= place.get("radius_km", 25):
            return True
    return True


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((phi2 - phi1) / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


async def _send_notification(settings, contact: Dict, alert: Dict) -> None:
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        body = (
            f"HAVEN ALERT: {alert.get('hazard_type', 'Emergency')} — "
            f"{alert.get('location_label', 'your area')}. "
            f"Severity: {alert.get('severity', '').upper()}."
        )
        client.messages.create(
            body=body,
            from_=settings.twilio_from_number,
            to=contact["phone"],
        )
        logger.info("SMS sent to %s for alert %s", contact["phone"], alert["id"])
    except Exception as exc:
        logger.error("SMS failed to %s: %s", contact.get("phone"), exc)
