import uuid
from typing import Any, Dict, List, Optional

from app.db.client import get_supabase

TABLE = "action_logs"


def create(user_id: str, action_type: str, payload: Dict[str, Any], requires_approval: bool = False) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action_type": action_type,
        "status": "pending",
        "payload_json": payload,
        "requires_approval": requires_approval,
        "approved": None,
    }
    result = get_supabase().table(TABLE).insert(row).execute()
    return result.data[0]


def update_status(action_id: str, status: str, result_json: Optional[Dict] = None) -> dict:
    updates: Dict[str, Any] = {"status": status}
    if result_json is not None:
        updates["result_json"] = result_json
    result = get_supabase().table(TABLE).update(updates).eq("id", action_id).execute()
    return result.data[0]


def approve(action_id: str, approved: bool) -> dict:
    result = (
        get_supabase()
        .table(TABLE)
        .update({"approved": approved, "status": "approved" if approved else "denied"})
        .eq("id", action_id)
        .execute()
    )
    return result.data[0]


def get(action_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("id", action_id)
        .maybe_single()
        .execute()
    )
    return result.data


def list_for_user(user_id: str, limit: int = 50) -> List[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
