"""
Session lifecycle management.

Owns: session creation, worker mapping, status transitions,
LiveKit room name generation.
"""
import logging
import uuid
from typing import Optional

from app.db.client import get_supabase

logger = logging.getLogger(__name__)

TABLE = "sessions"


def _room_name(session_id: str) -> str:
    return f"haven-{session_id[:8]}"


def create_session() -> dict:
    session_id = str(uuid.uuid4())
    room_name = _room_name(session_id)
    data = {
        "id": session_id,
        "status": "pending",
        "livekit_room_name": room_name,
    }
    result = get_supabase().table(TABLE).insert(data).execute()
    row = result.data[0]
    logger.info("Session created: %s  room=%s", session_id, room_name)
    return row


def get_session(session_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("id", session_id)
        .maybe_single()
        .execute()
    )
    return result.data


def attach_worker(session_id: str, worker_id: str) -> dict:
    result = (
        get_supabase()
        .table(TABLE)
        .update({"worker_id": worker_id, "status": "active"})
        .eq("id", session_id)
        .execute()
    )
    row = result.data[0]
    logger.info("Worker %s attached to session %s", worker_id, session_id)
    return row


def set_openai_session(session_id: str, openai_session_id: str) -> dict:
    result = (
        get_supabase()
        .table(TABLE)
        .update({"openai_session_id": openai_session_id})
        .eq("id", session_id)
        .execute()
    )
    return result.data[0]


def end_session(session_id: str) -> dict:
    from datetime import datetime, timezone

    result = (
        get_supabase()
        .table(TABLE)
        .update({"status": "ended", "ended_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", session_id)
        .execute()
    )
    logger.info("Session ended: %s", session_id)
    return result.data[0]
