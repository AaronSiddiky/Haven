# Escalation Rules — Haven Voice Agent

## Severity tiers and interrupt behavior

| Tier | Behavior |
|---|---|
| `clear` | No alerts — confirm and offer to check |
| `inform` | Mention if relevant, do not interrupt |
| `watch` | Notify at next natural turn |
| `warning` | Interrupt current conversation |
| `act_now` | Interrupt immediately, lead with action |

## Escalation announcement templates

### watch → warning
> "Update: the [hazard] Watch in [location] has been upgraded to a [hazard] Warning. [Recommended action]."

### warning → act_now
> "URGENT: The [hazard] Warning has escalated. [Location] — [critical action immediately]. Shall I [next step]?"

### New act_now (no prior alert)
> "URGENT — there is a [hazard] affecting [location]. [Single most critical action]. Shall I [open guidance / contact someone]?"

## Downgrade / resolution

> "Good news: the [hazard] alert for [location] has been lifted. All clear."

## Multiple alerts

1. Lead with highest severity
2. Group by location
3. Offer full list: "There are [N] active alerts. Want me to go through them?"

## Simultaneous act_now + pending user request

- Interrupt the current response
- State the act_now alert first
- Resume the user's original request after: "Now, back to your question..."
