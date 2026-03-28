"""
Server-Sent Events endpoint.

Connect with:
    const es = new EventSource(`/events/${sessionId}`)
    es.onmessage = (e) => { const event = JSON.parse(e.data); ... }
"""
import asyncio
import json
import logging

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.ws.manager import event_manager

logger = logging.getLogger(__name__)
router = APIRouter()
KEEPALIVE_SECONDS = 25


@router.get("/{session_id}")
async def session_events(session_id: str, request: Request):
    async def generator():
        q = event_manager.subscribe(session_id)
        logger.info("SSE client connected: session=%s", session_id)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=KEEPALIVE_SECONDS)
                    yield {"data": json.dumps(event)}
                except asyncio.TimeoutError:
                    yield {"data": json.dumps({"type": "ping"})}
        finally:
            event_manager.unsubscribe(session_id, q)
            logger.info("SSE client disconnected: session=%s", session_id)

    return EventSourceResponse(generator())
