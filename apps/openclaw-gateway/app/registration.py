"""
Auto-registration and heartbeat with the Haven API.

On startup the gateway registers itself as a worker.  A background
task sends heartbeats every 30 seconds.
"""
import asyncio
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_worker_id: Optional[str] = None
_heartbeat_task: Optional[asyncio.Task] = None
_session_id: Optional[str] = None


def get_worker_id() -> Optional[str]:
    return _worker_id


def get_session_id() -> Optional[str]:
    return _session_id


def set_session_id(sid: str) -> None:
    global _session_id
    _session_id = sid


async def register() -> str:
    global _worker_id
    settings = get_settings()
    payload = {
        "label": settings.gateway_label,
        "machine_name": settings.machine_name,
        "gateway_url": f"http://localhost:{settings.gateway_port}",
        "openclaw_mode": "openclaw",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(f"{settings.haven_api_url}/workers/register", json=payload)
        resp.raise_for_status()
        data = resp.json()
    _worker_id = data["id"]
    logger.info("Registered as worker %s", _worker_id)
    return _worker_id


async def _heartbeat_loop() -> None:
    settings = get_settings()
    while True:
        await asyncio.sleep(30)
        if not _worker_id:
            continue
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{settings.haven_api_url}/workers/heartbeat",
                    json={"worker_id": _worker_id},
                )
            logger.debug("Heartbeat sent for worker %s", _worker_id)
        except Exception as exc:
            logger.warning("Heartbeat failed: %s", exc)


def start_heartbeat() -> None:
    global _heartbeat_task
    _heartbeat_task = asyncio.create_task(_heartbeat_loop())


async def mark_offline() -> None:
    global _heartbeat_task
    if _heartbeat_task:
        _heartbeat_task.cancel()
        _heartbeat_task = None
    if not _worker_id:
        return
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{settings.haven_api_url}/workers/{_worker_id}/offline",
            )
    except Exception:
        pass
