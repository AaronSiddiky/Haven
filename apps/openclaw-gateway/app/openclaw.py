"""
OpenClaw client — forwards instructions to the local OpenClaw agent.

Communicates via POST /tools/invoke on the OpenClaw Gateway (port 18789).
Uses the `sessions_send` tool to inject messages into the agent session
and wait for a response.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

SEND_TIMEOUT = 120.0


def _openclaw_url() -> str:
    return get_settings().openclaw_url.rstrip("/")


def _headers() -> Dict[str, str]:
    settings = get_settings()
    h = {"Content-Type": "application/json"}
    if settings.openclaw_token:
        h["Authorization"] = f"Bearer {settings.openclaw_token}"
    return h


async def send_message(
    message: str,
    session_key: str = "main",
    timeout_seconds: int = 90,
) -> Dict[str, Any]:
    """
    Send a natural language instruction to OpenClaw via sessions_send.
    Waits up to timeout_seconds for the agent to finish, then returns the reply.
    """
    url = f"{_openclaw_url()}/tools/invoke"
    payload = {
        "tool": "sessions_send",
        "args": {
            "sessionKey": session_key,
            "message": message,
            "timeoutSeconds": timeout_seconds,
        },
    }

    logger.info("→ OpenClaw [%s]: %s", session_key, message[:120])

    async with httpx.AsyncClient(timeout=SEND_TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    if data.get("ok"):
        logger.info("← OpenClaw responded (session=%s)", session_key)
    else:
        logger.warning("← OpenClaw error: %s", data.get("error"))

    return data


async def invoke_tool(
    tool: str,
    args: Optional[Dict[str, Any]] = None,
    session_key: str = "main",
) -> Dict[str, Any]:
    """Invoke a specific OpenClaw tool directly via /tools/invoke."""
    url = f"{_openclaw_url()}/tools/invoke"
    payload: Dict[str, Any] = {"tool": tool, "sessionKey": session_key}
    if args:
        payload["args"] = args

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def health_check() -> Dict[str, Any]:
    """Check if OpenClaw is reachable by listing sessions."""
    url = f"{_openclaw_url()}/tools/invoke"
    payload = {"tool": "sessions_list", "args": {}}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload, headers=_headers())
            if resp.status_code == 200:
                return {"status": "ok"}
            return {"status": "auth_error", "code": resp.status_code}
    except Exception as exc:
        return {"status": "unreachable", "error": str(exc)}
