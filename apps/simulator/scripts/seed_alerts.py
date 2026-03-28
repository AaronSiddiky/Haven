"""
Seed Supabase with simulator scenarios for demo/testing.

Usage:
    python scripts/seed_alerts.py [--scenario flood-warning] [--all]

Reads scenarios from ../scenarios/*.json and inserts them as normalized_alerts.
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SCENARIOS_DIR = Path(__file__).parent.parent / "scenarios"

SEVERITY_MAP = {
    "Extreme": "act_now", "Severe": "warning",
    "Moderate": "watch", "Minor": "inform", "Unknown": "inform",
}
EVENT_OVERRIDES = {
    "Evacuation - Immediate": "act_now",
    "Flash Flood Warning": "warning",
    "Tornado Warning": "act_now",
    "Air Quality Alert": "inform",
}


def severity_from_props(props: dict) -> str:
    event = props.get("event", "")
    if event in EVENT_OVERRIDES:
        return EVENT_OVERRIDES[event]
    return SEVERITY_MAP.get(props.get("severity", "Unknown"), "inform")


def seed_scenario(db, scenario_path: Path) -> int:
    with open(scenario_path) as f:
        scenario = json.load(f)

    count = 0
    for alert in scenario.get("alerts", []):
        props = alert.get("properties", {})
        external_id = props.get("id") or props.get("@id") or ""
        if not external_id:
            continue

        existing = db.table("raw_alerts").select("id").eq("source_name", "NWS").eq("external_id", external_id).limit(1).execute()
        if existing.data:
            print(f"  ⏭  Already seeded: {external_id[:50]}")
            continue

        raw_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        db.table("raw_alerts").insert({
            "id": raw_id,
            "source_name": alert.get("source", "NWS"),
            "external_id": external_id,
            "payload_json": props,
            "fetched_at": now,
            "processed": False,
        }).execute()

        severity = severity_from_props(props)
        normalized = {
            "id": str(uuid.uuid4()),
            "raw_alert_id": raw_id,
            "headline": props.get("headline") or props.get("event", "Alert"),
            "location_label": props.get("areaDesc", "Demo area"),
            "hazard_type": props.get("event", "Unknown"),
            "severity": severity,
            "starts_at": props.get("onset") or props.get("effective"),
            "ends_at": props.get("expires") or props.get("ends"),
            "summary": f"{props.get('event', 'Alert')} — {props.get('areaDesc', 'Demo area')}.",
            "description": props.get("description", ""),
            "instruction": props.get("instruction"),
            "recommended_actions": [],
            "source": {
                "id": external_id,
                "name": alert.get("source", "NWS"),
                "url": props.get("@id"),
                "timestamp": now,
                "official": True,
            },
            "is_active": True,
            "fetched_at": now,
            "geometry": alert.get("geometry"),
        }

        db.table("normalized_alerts").insert(normalized).execute()
        db.table("raw_alerts").update({"processed": True}).eq("id", raw_id).execute()

        print(f"  ✓  Seeded [{severity:8}] {normalized['headline'][:60]}")
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Seed Haven simulator scenarios")
    parser.add_argument("--scenario", help="Scenario name (without .json)")
    parser.add_argument("--all", action="store_true", help="Seed all scenarios")
    args = parser.parse_args()

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not supabase_url or not supabase_key:
        print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
        sys.exit(1)

    db = create_client(supabase_url, supabase_key)

    if args.all:
        paths = list(SCENARIOS_DIR.glob("*.json"))
    elif args.scenario:
        paths = [SCENARIOS_DIR / f"{args.scenario}.json"]
    else:
        paths = list(SCENARIOS_DIR.glob("*.json"))

    total = 0
    for path in paths:
        if not path.exists():
            print(f"Scenario not found: {path}")
            continue
        print(f"\nSeeding: {path.name}")
        total += seed_scenario(db, path)

    print(f"\nDone — {total} alert(s) seeded.")


if __name__ == "__main__":
    main()
