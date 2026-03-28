"""
Job: expire_old_alerts

Marks normalized_alerts as inactive if their ends_at has passed.
"""
import logging
from datetime import datetime, timezone

from supabase import create_client

from src.settings import get_settings

logger = logging.getLogger(__name__)


async def run() -> None:
    settings = get_settings()
    db = create_client(settings.supabase_url, settings.supabase_service_key)

    now = datetime.now(timezone.utc).isoformat()
    result = (
        db.table("normalized_alerts")
        .update({"is_active": False})
        .eq("is_active", True)
        .lt("ends_at", now)
        .execute()
    )
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Expired %d old alerts", count)
