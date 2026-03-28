"""
Worker registry.

Tracks the friend's machine (OpenClaw host + screen publisher).
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.db.client import get_supabase

logger = logging.getLogger(__name__)

TABLE = "workers"


def register(
    label: str,
    machine_name: str,
    gateway_url: str,
    openclaw_mode: str = "openclaw",
) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "label": label,
        "machine_name": machine_name,
        "gateway_url": gateway_url,
        "openclaw_mode": openclaw_mode,
        "status": "idle",
        "screen_stream_status": "disconnected",
    }
    result = get_supabase().table(TABLE).insert(row).execute()
    logger.info("Worker registered: %s  machine=%s", row["id"], machine_name)
    return result.data[0]


def heartbeat(worker_id: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    result = (
        get_supabase()
        .table(TABLE)
        .update({"last_seen_at": now, "status": "idle"})
        .eq("id", worker_id)
        .execute()
    )
    return result.data[0]


def set_screen_ready(worker_id: str, session_id: Optional[str] = None) -> dict:
    result = (
        get_supabase()
        .table(TABLE)
        .update({"screen_stream_status": "connected", "status": "active"})
        .eq("id", worker_id)
        .execute()
    )
    logger.info("Worker %s screen ready", worker_id)
    return result.data[0]


def set_offline(worker_id: str) -> dict:
    result = (
        get_supabase()
        .table(TABLE)
        .update({"status": "offline", "screen_stream_status": "disconnected"})
        .eq("id", worker_id)
        .execute()
    )
    return result.data[0]


def get_worker(worker_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("id", worker_id)
        .maybe_single()
        .execute()
    )
    return result.data
