"""
Generates accessible plain-language summaries of alerts using OpenAI.
"""
import logging
from typing import Any, Dict

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def summarize_alert(alert: Dict[str, Any]) -> str:
    """
    Generate a short, accessible plain-language summary of an alert.
    Safe for screen readers and voice output.
    """
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    headline = alert.get("headline", "")
    description = alert.get("description", "")[:1000]
    hazard = alert.get("hazard_type", "")
    location = alert.get("location_label", "")
    severity = alert.get("severity", "")

    prompt = f"""Summarize this emergency alert in 2 sentences. 
Use plain language suitable for people with disabilities. Avoid jargon.
Be direct about the risk level and what action to take.

Alert: {hazard}
Location: {location}
Severity: {severity}
Details: {description}
"""

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Summary generation failed: %s", exc)
        return f"{headline} — {location}. Severity: {severity}."


async def summarize_for_voice(alert: Dict[str, Any]) -> str:
    """
    Generate a very short (1 sentence) summary optimized for voice TTS.
    """
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = f"""In one short sentence, describe this alert for a voice assistant.
Start with the hazard type, mention the location, and state the urgency.

Hazard: {alert.get('hazard_type', '')}
Location: {alert.get('location_label', '')}
Severity: {alert.get('severity', '')}
Headline: {alert.get('headline', '')}
"""

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Voice summary failed: %s", exc)
        return alert.get("headline", "Emergency alert in your area.")
