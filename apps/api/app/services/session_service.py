"""
Session lifecycle — LiveKit room creation and worker attachment.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.db.client import get_supabase

logger = logging.getLogger(__name__)
TABLE = "sessions"


def _room_name(session_id: str) -> str:
    return f"haven-{session_id[:8]}"


def create_session() -> dict:
    session_id = str(uuid.uuid4())
    room_name = _room_name(session_id)
    result = get_supabase().table(TABLE).insert({
        "id": session_id, "status": "pending", "livekit_room_name": room_name,
    }).execute()
    logger.info("Session created: %s  room=%s", session_id, room_name)
    return result.data[0]


def get_session(session_id: str) -> Optional[dict]:
    result = (
        get_supabase().table(TABLE).select("*").eq("id", session_id).maybe_single().execute()
    )
    return result.data


def attach_worker(session_id: str, worker_id: str) -> dict:
    result = (
        get_supabase().table(TABLE)
        .update({"worker_id": worker_id, "status": "active"})
        .eq("id", session_id).execute()
    )
    logger.info("Worker %s attached to session %s", worker_id, session_id)
    return result.data[0]


def set_openai_session(session_id: str, openai_session_id: str) -> dict:
    result = (
        get_supabase().table(TABLE)
        .update({"openai_session_id": openai_session_id})
        .eq("id", session_id).execute()
    )
    return result.data[0]


def end_session(session_id: str) -> dict:
    result = (
        get_supabase().table(TABLE)
        .update({"status": "ended", "ended_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", session_id).execute()
    )
    logger.info("Session ended: %s", session_id)
    return result.data[0]
