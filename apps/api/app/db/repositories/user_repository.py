import uuid
from typing import Optional

from app.db.client import get_supabase

CONTACTS = "emergency_contacts"
PREFS = "user_preferences"


def get_contacts(user_id: str) -> list:
    result = (
        get_supabase().table(CONTACTS).select("*").eq("user_id", user_id).execute()
    )
    return result.data


def create_contact(user_id: str, data: dict) -> dict:
    row = {"id": str(uuid.uuid4()), "user_id": user_id, **data}
    result = get_supabase().table(CONTACTS).insert(row).execute()
    return result.data[0]


def get_contact(contact_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(CONTACTS)
        .select("*")
        .eq("id", contact_id)
        .maybe_single()
        .execute()
    )
    return result.data


def update_contact(contact_id: str, data: dict) -> dict:
    result = (
        get_supabase().table(CONTACTS).update(data).eq("id", contact_id).execute()
    )
    return result.data[0]


def delete_contact(contact_id: str) -> None:
    get_supabase().table(CONTACTS).delete().eq("id", contact_id).execute()


def get_preferences(user_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(PREFS)
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data


def upsert_preferences(user_id: str, data: dict) -> dict:
    row = {"id": str(uuid.uuid4()), "user_id": user_id, **data}
    result = get_supabase().table(PREFS).upsert(row, on_conflict="user_id").execute()
    return result.data[0]
