"""
National Weather Service (NWS) API client.

No API key required. Uses CAP/GeoJSON format.
Docs: https://www.weather.gov/documentation/services-web-api
"""
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.weather.gov"
HEADERS = {
    "User-Agent": "(HavenApp/1.0, contact@haven.app)",
    "Accept": "application/geo+json",
}
TIMEOUT = 15.0


async def get_active_alerts_by_state(state: str) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/alerts/active?area={state.upper()}"
    return await _get_features(url)


async def get_active_alerts_by_point(lat: float, lon: float) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/alerts/active?point={lat:.4f},{lon:.4f}"
    return await _get_features(url)


async def get_active_alerts_by_zone(zone_id: str) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/alerts/active?zone={zone_id}"
    return await _get_features(url)


async def get_alert(alert_id: str) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}/alerts/{alert_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise


async def _get_features(url: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    features = data.get("features", [])
    logger.debug("NWS returned %d features from %s", len(features), url)
    return features
