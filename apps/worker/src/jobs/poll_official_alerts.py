"""
Job: poll_official_alerts

Fetches active NWS alerts for all configured states, normalizes them,
and persists only new alerts to Supabase.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
from supabase import create_client

from src.settings import get_settings
from src.jobs._normalizer import normalize_nws_feature, severity_from_nws

logger = logging.getLogger(__name__)

NWS_BASE = "https://api.weather.gov"
NWS_HEADERS = {
    "User-Agent": "(HavenWorker/1.0, contact@haven.app)",
    "Accept": "application/geo+json",
}


async def run() -> None:
    settings = get_settings()
    db = create_client(settings.supabase_url, settings.supabase_service_key)

    total_new = 0
    for state in settings.states_list:
        try:
            features = await _fetch_state(state)
            new_count = await _ingest(db, features)
            total_new += new_count
            logger.info("NWS poll: state=%s  features=%d  new=%d", state, len(features), new_count)
        except Exception as exc:
            logger.error("NWS poll failed for %s: %s", state, exc)

    logger.info("NWS poll complete — total new alerts: %d", total_new)


async def _fetch_state(state: str) -> List[Dict[str, Any]]:
    url = f"{NWS_BASE}/alerts/active?area={state.upper()}"
    async with httpx.AsyncClient(timeout=15.0, headers=NWS_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json().get("features", [])


async def _ingest(db, features: List[Dict[str, Any]]) -> int:
    new_count = 0
    for feature in features:
        props = feature.get("properties", {})
        external_id = props.get("id") or props.get("@id") or ""
        if not external_id:
            continue

        existing = db.table("raw_alerts").select("id").eq("source_name", "NWS").eq("external_id", external_id).limit(1).execute()
        if existing.data:
            continue

        try:
            raw_id = str(uuid.uuid4())
            db.table("raw_alerts").insert({
                "id": raw_id,
                "source_name": "NWS",
                "external_id": external_id,
                "payload_json": props,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "processed": False,
            }).execute()

            normalized = normalize_nws_feature(feature, raw_id)
            db.table("normalized_alerts").upsert(normalized).execute()
            db.table("raw_alerts").update({"processed": True}).eq("id", raw_id).execute()
            new_count += 1
        except Exception as exc:
            logger.error("Failed to ingest %s: %s", external_id, exc)

    return new_count
