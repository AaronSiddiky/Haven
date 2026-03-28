"""
Fetches and surfaces official guidance URLs for active alerts.
"""
import logging
from typing import Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

OFFICIAL_SOURCES = {
    "Flood": "https://www.ready.gov/floods",
    "Flash Flood": "https://www.ready.gov/floods",
    "Tornado": "https://www.ready.gov/tornadoes",
    "Hurricane": "https://www.ready.gov/hurricanes",
    "Earthquake": "https://www.ready.gov/earthquakes",
    "Wildfire": "https://www.ready.gov/wildfires",
    "Winter Storm": "https://www.ready.gov/winter-weather",
    "Blizzard": "https://www.ready.gov/winter-weather",
    "Extreme Heat": "https://www.ready.gov/heat",
    "Tsunami": "https://www.ready.gov/tsunamis",
    "Hazardous Materials": "https://www.ready.gov/hazardous-materials-incidents",
    "Evacuation": "https://www.ready.gov/evacuating-yourself-and-your-family",
}

NWS_ALERT_SEARCH = "https://www.weather.gov/search/?query={query}"


def get_guidance_url(hazard_type: str, location: str) -> str:
    """Return the best official guidance URL for a given hazard type."""
    for key, url in OFFICIAL_SOURCES.items():
        if key.lower() in hazard_type.lower():
            return url

    query = quote(f"{hazard_type} {location}")
    return NWS_ALERT_SEARCH.format(query=query)


def get_nws_alert_url(alert_id: str) -> Optional[str]:
    """Return the direct NWS URL for an alert by its CAP ID."""
    if alert_id.startswith("urn:oid:"):
        return f"https://api.weather.gov/alerts/{alert_id}"
    return None


def guidance_for_alert(alert: dict) -> dict:
    """Return guidance links and instructions for a normalized alert."""
    hazard = alert.get("hazard_type", "")
    location = alert.get("location_label", "")
    source = alert.get("source", {})

    guidance_url = get_guidance_url(hazard, location)
    source_url = source.get("url") or get_nws_alert_url(source.get("id", ""))

    return {
        "guidance_url": guidance_url,
        "source_url": source_url,
        "instruction": alert.get("instruction"),
        "recommended_actions": alert.get("recommended_actions", []),
    }
