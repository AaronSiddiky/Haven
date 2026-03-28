"""
Transcript storage.

Persists turns from the OpenAI Realtime session so the user
can review the conversation and so the backend has a persistent record.
"""
import logging
import uuid
from typing import List

from app.db.client import get_supabase

logger = logging.getLogger(__name__)

TABLE = "transcript_turns"


def add_turn(session_id: str, speaker: str, text: str) -> dict:
    if speaker not in ("user", "assistant"):
        raise ValueError(f"Invalid speaker: {speaker}")
    row = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "speaker": speaker,
        "text": text,
    }
    result = get_supabase().table(TABLE).insert(row).execute()
    return result.data[0]


def get_turns(session_id: str) -> List[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("session_id", session_id)
        .order("timestamp")
        .execute()
    )
    return result.data
