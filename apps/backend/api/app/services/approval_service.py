"""
Approval gate.

High-consequence actions (purchase, booking, call) must be
approved here before OpenClaw proceeds.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.client import get_supabase
from app.services import status_event_service

logger = logging.getLogger(__name__)

TABLE = "approvals"


async def create_approval(
    session_id: str,
    action_type: str,
    payload: Dict[str, Any],
) -> dict:
    approval_id = str(uuid.uuid4())
    row = {
        "id": approval_id,
        "session_id": session_id,
        "action_type": action_type,
        "payload_json": payload,
        "status": "pending",
    }
    result = get_supabase().table(TABLE).insert(row).execute()
    row = result.data[0]

    await status_event_service.publish(
        session_id,
        "approval.requested",
        {
            "approval_id": approval_id,
            "action_type": action_type,
            "label": _label(action_type, payload),
        },
    )
    logger.info("Approval requested: %s  action=%s", approval_id, action_type)
    return row


def _label(action_type: str, payload: Dict[str, Any]) -> str:
    labels = {
        "book_transport": "Book transport option?",
        "make_purchase": "Confirm purchase?",
        "initiate_call": "Place call or send message?",
        "open_account_page": "Open account page?",
    }
    return labels.get(action_type, f"Approve: {action_type}?")


async def resolve(
    approval_id: str,
    status: str,
    reason: Optional[str] = None,
) -> dict:
    if status not in ("approved", "denied"):
        raise ValueError(f"Invalid approval status: {status}")

    now = datetime.now(timezone.utc).isoformat()
    result = (
        get_supabase()
        .table(TABLE)
        .update({"status": status, "resolved_at": now})
        .eq("id", approval_id)
        .execute()
    )
    row = result.data[0]

    await status_event_service.publish(
        row["session_id"],
        "approval.resolved",
        {"approval_id": approval_id, "status": status, "reason": reason},
    )
    logger.info("Approval %s → %s", approval_id, status)
    return row


def get_pending(session_id: str) -> List[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("session_id", session_id)
        .eq("status", "pending")
        .order("requested_at")
        .execute()
    )
    return result.data


def get_approval(approval_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("id", approval_id)
        .maybe_single()
        .execute()
    )
    return result.data
