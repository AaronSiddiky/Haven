"""
Tool: open_evacuation_page

Opens the official evacuation/guidance page on the remote browser via OpenClaw.
REQUIRES USER APPROVAL — this is an external browser action.
"""
import logging
from typing import Any, Dict

import httpx

from app.core.config import get_settings
from app.db.repositories import alert_repository
from app.services import official_guidance_service

logger = logging.getLogger(__name__)


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    alert_id: str = args["alert_id"]
    session_id: str = args.get("session_id", "")

    alert = alert_repository.get_alert(alert_id)
    if not alert:
        return {"error": f"Alert {alert_id} not found."}

    guidance = official_guidance_service.guidance_for_alert(alert)
    url = guidance["guidance_url"]

    settings = get_settings()
    if not settings.openclaw_gateway_url:
        return {
            "status": "no_openclaw",
            "guidance_url": url,
            "message": "OpenClaw not configured. Share this URL with the user.",
        }

    try:
        headers = {}
        if settings.openclaw_api_key:
            headers["Authorization"] = f"Bearer {settings.openclaw_api_key}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{settings.openclaw_gateway_url}/execute",
                json={"tool": "open_url", "params": {"url": url, "session_id": session_id}},
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()

        logger.info("Evacuation page opened via OpenClaw: %s", url)
        return {
            "status": "opened",
            "url": url,
            "run_id": result.get("run_id"),
            "message": f"Opening {alert.get('hazard_type', 'guidance')} page on the remote browser.",
        }
    except Exception as exc:
        logger.error("OpenClaw open_url failed: %s", exc)
        return {
            "status": "error",
            "guidance_url": url,
            "message": f"Could not open the page automatically. URL: {url}",
        }
