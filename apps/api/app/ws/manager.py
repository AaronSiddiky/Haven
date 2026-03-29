"""
In-process SSE event bus.

Routes publish events here; the /events/{session_id} SSE endpoint
drains them per connected client.
"""
import asyncio
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class EventManager:
    def __init__(self) -> None:
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, session_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._listeners.setdefault(session_id, []).append(q)
        logger.debug("SSE subscriber added for session %s", session_id)
        return q

    def unsubscribe(self, session_id: str, q: asyncio.Queue) -> None:
        listeners = self._listeners.get(session_id, [])
        if q in listeners:
            listeners.remove(q)
        if not listeners:
            self._listeners.pop(session_id, None)
        logger.debug("SSE subscriber removed for session %s", session_id)

    async def publish(self, session_id: str, event_type: str, data: dict) -> None:
        payload = {"type": event_type, "session_id": session_id, **data}
        listeners = self._listeners.get(session_id, [])
        for q in listeners:
            await q.put(payload)
        logger.debug(
            "Published event '%s' to %d listeners for session %s",
            event_type, len(listeners), session_id,
        )

    async def broadcast(self, event_type: str, data: dict) -> None:
        """Push an event to ALL connected SSE sessions."""
        payload = {"type": event_type, **data}
        total = 0
        for session_id, queues in self._listeners.items():
            for q in queues:
                await q.put(payload)
                total += 1
        logger.info("Broadcast '%s' to %d listeners across %d sessions",
                     event_type, total, len(self._listeners))

    def serialize(self, payload: dict) -> str:
        return json.dumps(payload)


event_manager = EventManager()
