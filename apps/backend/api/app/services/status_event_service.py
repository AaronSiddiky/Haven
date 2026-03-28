"""
Frontend event broadcasting.

Thin facade over the in-process EventManager.
All services import from here so the event schema stays central.
"""
from typing import Any, Dict

from app.ws.manager import event_manager


async def publish(session_id: str, event_type: str, data: Dict[str, Any] = {}) -> None:
    await event_manager.publish(session_id, event_type, data)


async def session_ready(session_id: str, room_name: str) -> None:
    await publish(session_id, "session.ready", {"room_name": room_name})


async def worker_connected(session_id: str, worker_id: str) -> None:
    await publish(session_id, "worker.connected", {"worker_id": worker_id})


async def screen_connected(session_id: str, participant: str = "haven-worker") -> None:
    await publish(session_id, "screen.connected", {"participant": participant})


async def agent_status(session_id: str, text: str) -> None:
    await publish(session_id, "agent.status", {"text": text})


async def approval_requested(session_id: str, approval_id: str, label: str) -> None:
    await publish(
        session_id,
        "approval.requested",
        {"approval_id": approval_id, "label": label},
    )


async def worker_disconnected(session_id: str, worker_id: str) -> None:
    await publish(session_id, "worker.disconnected", {"worker_id": worker_id})
