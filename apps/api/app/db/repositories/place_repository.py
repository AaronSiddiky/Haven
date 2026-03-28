import uuid
from typing import List, Optional

from app.db.client import get_supabase

TABLE = "monitored_places"


def create(user_id: str, data: dict) -> dict:
    row = {"id": str(uuid.uuid4()), "user_id": user_id, **data}
    result = get_supabase().table(TABLE).insert(row).execute()
    return result.data[0]


def list_for_user(user_id: str) -> List[dict]:
    result = (
        get_supabase().table(TABLE).select("*").eq("user_id", user_id).execute()
    )
    return result.data


def get(place_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(TABLE)
        .select("*")
        .eq("id", place_id)
        .maybe_single()
        .execute()
    )
    return result.data


def update(place_id: str, data: dict) -> dict:
    result = (
        get_supabase().table(TABLE).update(data).eq("id", place_id).execute()
    )
    return result.data[0]


def delete(place_id: str) -> None:
    get_supabase().table(TABLE).delete().eq("id", place_id).execute()
