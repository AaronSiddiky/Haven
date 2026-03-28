"""
HTTP client for the OpenClaw remote Gateway.

The gateway runs on the worker's machine (friend's computer).
All calls are async fire-and-poll; long-running browser tasks
return a run_id that the caller can poll via get_run().
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

TIMEOUT = 30.0


def _headers() -> Dict[str, str]:
    settings = get_settings()
    headers = {"Content-Type": "application/json"}
    if settings.openclaw_api_key:
        headers["Authorization"] = f"Bearer {settings.openclaw_api_key}"
    return headers


def _base_url(gateway_url: Optional[str] = None) -> str:
    return gateway_url or get_settings().openclaw_gateway_url


async def execute_task(
    tool_name: str,
    params: Dict[str, Any],
    gateway_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Dispatch a browser task to OpenClaw. Returns {run_id, status}."""
    url = f"{_base_url(gateway_url)}/execute"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json={"tool": tool_name, "params": params}, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def get_run(run_id: str, gateway_url: Optional[str] = None) -> Dict[str, Any]:
    """Poll the status of a running task."""
    url = f"{_base_url(gateway_url)}/runs/{run_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def cancel_run(run_id: str, gateway_url: Optional[str] = None) -> Dict[str, Any]:
    """Cancel an in-progress task."""
    url = f"{_base_url(gateway_url)}/cancel"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json={"run_id": run_id}, headers=_headers())
        resp.raise_for_status()
        return resp.json()
