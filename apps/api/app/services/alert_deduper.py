"""
Deduplication logic for normalized alerts.

Two alerts are considered duplicates if they have the same:
  - hazard_type
  - location_label (fuzzy)
  - overlapping time window
  - same source
"""
from datetime import timedelta
from typing import List


def _overlap(a_start, a_end, b_start, b_end) -> bool:
    if not (a_start and b_start):
        return False
    a_end = a_end or (a_start + timedelta(hours=24))
    b_end = b_end or (b_start + timedelta(hours=24))
    return a_start < b_end and b_start < a_end


def is_duplicate(candidate: dict, existing: List[dict]) -> bool:
    """Return True if candidate is a near-duplicate of any existing alert."""
    for alert in existing:
        if (
            alert.get("hazard_type") == candidate.get("hazard_type")
            and alert.get("source", {}).get("name") == candidate.get("source", {}).get("name")
            and _location_match(alert.get("location_label", ""), candidate.get("location_label", ""))
            and _overlap(
                alert.get("starts_at"),
                alert.get("ends_at"),
                candidate.get("starts_at"),
                candidate.get("ends_at"),
            )
        ):
            return True
    return False


def _location_match(a: str, b: str) -> bool:
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens or not b_tokens:
        return False
    overlap = len(a_tokens & b_tokens)
    return overlap / max(len(a_tokens), len(b_tokens)) >= 0.5


def dedupe(alerts: List[dict]) -> List[dict]:
    """Filter a list of alerts, removing duplicates. Keeps the most severe."""
    seen: List[dict] = []
    for alert in sorted(alerts, key=lambda a: a.get("severity", ""), reverse=True):
        if not is_duplicate(alert, seen):
            seen.append(alert)
    return seen
