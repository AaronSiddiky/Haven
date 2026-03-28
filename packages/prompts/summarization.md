# Summarization Prompt — Haven

## Purpose

Convert raw NWS alert text into short, accessible summaries for:
- Dashboard cards (2 sentences)
- Voice output (1 sentence)
- SMS notifications (140 chars)

## Dashboard card summary (2 sentences)

**Input variables:** `hazard_type`, `location_label`, `severity`, `description` (first 500 chars)

**Prompt:**
```
Summarize this emergency alert in exactly 2 sentences for a dashboard card.
Use plain language suitable for people with disabilities.
State the hazard, location, and what action to take.
Do not use meteorological jargon or abbreviations.

Hazard: {hazard_type}
Location: {location_label}
Severity: {severity}
Details: {description}
```

**Target output:** 25–45 words

## Voice summary (1 sentence)

**Input variables:** `hazard_type`, `location_label`, `severity`, `headline`

**Prompt:**
```
In one short sentence, describe this alert for voice output.
Start with the hazard, mention the location, and state the urgency.
Maximum 20 words. No jargon.

Hazard: {hazard_type}
Location: {location_label}
Severity: {severity}
```

**Target output:** 12–20 words

## SMS summary (140 chars)

**Format:**
```
HAVEN: {hazard_type} — {location} ({severity_label}). {action}.
```

**Severity labels for SMS:**
- `act_now` → EVACUATE NOW
- `warning` → Take protective action
- `watch` → Stay alert
- `inform` → FYI

## Quality rules

- Never exceed the target length
- If the source text is unclear, use: "[Hazard] in [location]. Check official sources."
- Never invent details not in the source data
- Always end with an action or next step
