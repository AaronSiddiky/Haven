"""
OpenClaw gateway client.

Sends natural language instructions to the gateway, which delegates
to browser-use. We do NOT control the browser — OpenClaw does.
"""
import logging
from typing import Any, Dict

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
TIMEOUT = 60.0


def _base_url() -> str:
    return get_settings().openclaw_gateway_url


def _headers() -> Dict[str, str]:
    key = get_settings().openclaw_api_key
    h = {"Content-Type": "application/json"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


async def execute(instruction: str, session_id: str = "") -> Dict[str, Any]:
    """Send a natural language instruction to the gateway."""
    base = _base_url()
    if not base:
        logger.warning("OpenClaw gateway URL not configured.")
        return {"status": "not_configured"}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{base}/execute",
            json={"instruction": instruction, "session_id": session_id},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_run(run_id: str) -> Dict[str, Any]:
    base = _base_url()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{base}/runs/{run_id}", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def cancel_run(run_id: str) -> Dict[str, Any]:
    base = _base_url()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{base}/cancel", json={"run_id": run_id}, headers=_headers()
        )
        resp.raise_for_status()
        return resp.json()
