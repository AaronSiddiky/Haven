import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.client import get_supabase

RAW = "raw_alerts"
NORM = "normalized_alerts"


def insert_raw(source_name: str, external_id: str, payload: Dict[str, Any]) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "source_name": source_name,
        "external_id": external_id,
        "payload_json": payload,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "processed": False,
    }
    result = get_supabase().table(RAW).insert(row).execute()
    return result.data[0]


def raw_exists(source_name: str, external_id: str) -> bool:
    result = (
        get_supabase()
        .table(RAW)
        .select("id")
        .eq("source_name", source_name)
        .eq("external_id", external_id)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def mark_raw_processed(raw_id: str) -> None:
    get_supabase().table(RAW).update({"processed": True}).eq("id", raw_id).execute()


def upsert_normalized(alert: Dict[str, Any]) -> dict:
    result = get_supabase().table(NORM).upsert(alert).execute()
    return result.data[0]


def get_active_alerts(limit: int = 50) -> List[dict]:
    result = (
        get_supabase()
        .table(NORM)
        .select("*")
        .eq("is_active", True)
        .order("fetched_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def get_alert(alert_id: str) -> Optional[dict]:
    result = (
        get_supabase()
        .table(NORM)
        .select("*")
        .eq("id", alert_id)
        .maybe_single()
        .execute()
    )
    return result.data


def expire_old_alerts(before: datetime) -> int:
    result = (
        get_supabase()
        .table(NORM)
        .update({"is_active": False})
        .eq("is_active", True)
        .lt("ends_at", before.isoformat())
        .execute()
    )
    return len(result.data)


def get_alerts_for_location(lat: float, lon: float, radius_km: float = 25.0) -> List[dict]:
    return get_active_alerts(limit=100)
