"""
Twilio SMS and voice call client.
"""
import logging
from typing import Any, Dict

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_sms(to: str, body: str) -> Dict[str, Any]:
    """Send an SMS to a phone number. Returns Twilio message SID."""
    settings = get_settings()

    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning("Twilio not configured — SMS not sent to %s", to)
        return {"sid": "SIMULATED", "status": "simulated", "to": to, "body": body}

    from twilio.rest import Client

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    message = client.messages.create(
        body=body,
        from_=settings.twilio_from_number,
        to=to,
    )
    logger.info("SMS sent to %s  sid=%s", to, message.sid)
    return {"sid": message.sid, "status": message.status, "to": to}


async def initiate_call(to: str, twiml_url: str) -> Dict[str, Any]:
    """Initiate a voice call using a TwiML URL for instructions."""
    settings = get_settings()

    if not settings.twilio_account_sid:
        return {"sid": "SIMULATED", "status": "simulated", "to": to}

    from twilio.rest import Client

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    call = client.calls.create(url=twiml_url, from_=settings.twilio_from_number, to=to)
    logger.info("Call initiated to %s  sid=%s", to, call.sid)
    return {"sid": call.sid, "status": call.status, "to": to}
