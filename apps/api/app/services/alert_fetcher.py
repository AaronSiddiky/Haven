"""
Fetches raw alerts from official sources and persists them.

Currently supported:
  - NWS (National Weather Service) — no API key required
"""
import logging
from typing import Any, Dict, List

import httpx

from app.db.repositories import alert_repository
from app.services.alert_normalizer import from_nws_feature

logger = logging.getLogger(__name__)

NWS_BASE = "https://api.weather.gov"
NWS_HEADERS = {
    "User-Agent": "(HavenApp, contact@haven.app)",
    "Accept": "application/geo+json",
}


async def fetch_nws_by_state(state: str) -> List[Dict[str, Any]]:
    """Fetch active NWS alerts for a US state code (e.g. 'CA', 'TX')."""
    url = f"{NWS_BASE}/alerts/active?area={state.upper()}"
    async with httpx.AsyncClient(timeout=15.0, headers=NWS_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return data.get("features", [])


async def fetch_nws_by_point(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Fetch active NWS alerts for a lat/lon point."""
    url = f"{NWS_BASE}/alerts/active?point={lat:.4f},{lon:.4f}"
    async with httpx.AsyncClient(timeout=15.0, headers=NWS_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return data.get("features", [])


async def ingest_nws_features(features: List[Dict[str, Any]]) -> int:
    """Normalize and persist new NWS features. Returns count of new alerts ingested."""
    ingested = 0
    for feature in features:
        props = feature.get("properties", {})
        external_id = props.get("id") or props.get("@id") or ""

        if not external_id:
            continue

        if alert_repository.raw_exists("NWS", external_id):
            continue

        try:
            raw = alert_repository.insert_raw("NWS", external_id, props)
            normalized = from_nws_feature(feature, raw_id=raw["id"])

            alert_dict = normalized.model_dump(mode="json")
            alert_dict["id"] = str(alert_dict["id"])
            alert_dict["source"] = alert_dict["source"]

            alert_repository.upsert_normalized(alert_dict)
            alert_repository.mark_raw_processed(raw["id"])
            ingested += 1
        except Exception as exc:
            logger.error("Failed to ingest NWS feature %s: %s", external_id, exc)

    logger.info("NWS ingest: %d new alerts", ingested)
    return ingested


async def run_nws_poll(states: List[str]) -> int:
    """Poll NWS for all given states. Returns total new alerts ingested."""
    total = 0
    for state in states:
        try:
            features = await fetch_nws_by_state(state)
            total += await ingest_nws_features(features)
        except Exception as exc:
            logger.error("NWS poll failed for state %s: %s", state, exc)
    return total
