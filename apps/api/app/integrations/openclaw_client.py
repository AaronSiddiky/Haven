"""
OpenClaw remote gateway client.

Routes browser automation tasks to the OpenClaw instance running
on the worker machine.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
TIMEOUT = 20.0


def _base_url() -> str:
    return get_settings().openclaw_gateway_url


def _headers() -> Dict[str, str]:
    key = get_settings().openclaw_api_key
    h = {"Content-Type": "application/json"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


async def open_url(url: str, session_id: str = "") -> Dict[str, Any]:
    """Tell OpenClaw to navigate the remote browser to a URL."""
    return await _execute("open_url", {"url": url, "session_id": session_id})


async def search(query: str, session_id: str = "") -> Dict[str, Any]:
    """Tell OpenClaw to perform a web search on the remote browser."""
    return await _execute("search", {"query": query, "session_id": session_id})


async def _execute(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    base = _base_url()
    if not base:
        logger.warning("OpenClaw gateway URL not configured.")
        return {"status": "not_configured", "run_id": None}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{base}/execute",
            json={"tool": tool, "params": params},
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
