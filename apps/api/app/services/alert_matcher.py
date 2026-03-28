"""
Matches active alerts to users based on their monitored places.
"""
import logging
import math
from typing import List, Tuple

from app.db.repositories import alert_repository, place_repository

logger = logging.getLogger(__name__)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def alerts_for_user(user_id: str) -> List[dict]:
    """
    Return all active alerts that intersect at least one of the user's monitored places.
    Fallback: returns all active alerts if the user has no places configured.
    """
    places = place_repository.list_for_user(user_id)
    all_alerts = alert_repository.get_active_alerts(limit=200)

    if not places:
        return all_alerts

    matched: List[Tuple[dict, float]] = []
    seen_ids = set()

    for alert in all_alerts:
        for place in places:
            if _alert_covers_place(alert, place):
                if alert["id"] not in seen_ids:
                    distance = 0.0
                    matched.append((alert, distance))
                    seen_ids.add(alert["id"])

    return [a for a, _ in matched]


def _alert_covers_place(alert: dict, place: dict) -> bool:
    """
    Check if an alert's geometry intersects a monitored place radius.
    Falls back to True (show all) when no geometry data is available.
    """
    geometry = alert.get("geometry")
    if not geometry:
        return True

    place_lat = place.get("lat", 0.0)
    place_lon = place.get("lon", 0.0)
    radius_km = place.get("radius_km", 25.0)

    geo_type = geometry.get("type", "")
    coords = geometry.get("coordinates", [])

    if geo_type == "Point" and len(coords) >= 2:
        dist = _haversine_km(place_lat, place_lon, coords[1], coords[0])
        return dist <= radius_km

    return True
