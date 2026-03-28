# Alert Lifecycle — Haven

## Overview

```
NWS API → fetch → raw_alerts → normalize → normalized_alerts → match → user
                                                  │
                                              classify
                                              dedupe
                                              expire
```

## Stages

### 1. Fetch

**Who:** `apps/worker/src/jobs/poll_official_alerts.py`  
**When:** Every 5 minutes  
**What:** `GET https://api.weather.gov/alerts/active?area={STATE}`  
**Output:** Raw NWS GeoJSON FeatureCollection

Skip if `external_id` already exists in `raw_alerts` (idempotent).

### 2. Persist raw

Insert to `raw_alerts` with `processed = false`.  
Keeps the original source payload for debugging and audit.

### 3. Normalize

**Who:** `apps/api/app/services/alert_normalizer.py`  
**What:** Convert NWS CAP properties → `NormalizedAlert` schema

Key transformations:
- `properties.severity` + `properties.urgency` + `properties.event` → `AlertSeverity` tier
- `properties.areaDesc` → `location_label`
- `properties.onset` / `properties.expires` → `starts_at` / `ends_at`
- `properties.response` → `recommended_actions[]`

### 4. Classify

**Who:** `apps/api/app/services/alert_classifier.py`  
**What:** Map to Haven severity tiers

Priority order:
1. Event-type overrides (e.g., `Tornado Warning` → always `act_now`)
2. NWS severity map (`Severe` → `warning`)
3. Urgency boost (`Immediate` +1 tier, `Future` -1 tier)

### 5. Dedupe

**Who:** `apps/api/app/services/alert_deduper.py`  
**What:** Suppress duplicate alerts from the same source/area/hazard with overlapping time windows.

Keeps the highest-severity version when duplicates exist.

### 6. Persist normalized

Insert to `normalized_alerts` with `is_active = true`.  
Mark `raw_alerts.processed = true`.

### 7. Match to users

**Who:** `apps/api/app/services/alert_matcher.py`  
**When:** On `GET /alerts/active?user_id=...` or voice tool call  
**What:** Filter active alerts to those overlapping the user's `monitored_places` by haversine distance

Fallback: if a user has no saved places, return all active alerts.

### 8. Surface

- Dashboard: via `GET /alerts/active`
- Voice: via `get_active_alerts` tool call
- SMS: via `notify_users` worker job

### 9. Expire

**Who:** `apps/worker/src/jobs/expire_old_alerts.py`  
**When:** Every 10 minutes  
**What:** Set `is_active = false` where `ends_at < now()`

### 10. Resolve

When an alert is cancelled or superseded:
- NWS `messageType = Cancel` → expire the referenced alert
- NWS `messageType = Update` → upsert normalized alert (new `external_id`)

## Severity mapping quick reference

| NWS Severity | NWS Urgency | Haven Tier |
|---|---|---|
| Extreme | Immediate | act_now |
| Severe | Immediate | act_now |
| Severe | Expected | warning |
| Moderate | Expected | watch |
| Minor | Any | inform |

**Event overrides always win over the generic table.**
