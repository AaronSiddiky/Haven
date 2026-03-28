# Haven

Voice-first emergency alert assistant for people with disabilities.

Haven monitors official alert feeds (NWS), explains active threats in plain language via a voice agent, and takes actions — opening guidance pages, contacting emergency contacts — with explicit user approval.

## Stack

- **Voice** — OpenAI Realtime API (WebRTC, browser-direct)
- **Alerts** — NWS public API (no key required)
- **Database** — Supabase (Postgres)
- **Browser automation** — OpenClaw
- **Notifications** — Twilio SMS
- **Screen share** — LiveKit

## Monorepo structure

```
haven/
├── apps/
│   ├── api/              # Unified FastAPI backend
│   │   ├── app/
│   │   │   ├── agents/       # Tool registry, session manager, 6 tool handlers
│   │   │   ├── integrations/ # NWS, OpenAI Realtime, LiveKit, Twilio, OpenClaw
│   │   │   ├── routes/       # alerts, voice, sessions, workers, livekit, events, …
│   │   │   ├── services/     # Alert pipeline (fetch → normalize → classify → match)
│   │   │   └── db/           # Supabase client + repositories
│   │   └── sql/schema.sql    # Run once in Supabase SQL editor
│   ├── worker/           # Background jobs (APScheduler)
│   │   └── src/jobs/         # poll_official_alerts, expire_old_alerts, notify_users
│   ├── simulator/        # Demo scenarios + seed script
│   │   └── scenarios/        # flood-warning, evacuation-order, conflicting-signals
│   └── web/              # Next.js frontend (dashboard + voice UI)
├── packages/
│   ├── shared-types/     # TypeScript contracts (NormalizedAlert, ActionLog, …)
│   └── prompts/          # Versioned agent prompts (voice-agent, escalation, safety)
└── docs/                 # architecture, alert-lifecycle, voice-flow
```

## Alert severity tiers

| Tier | Meaning | Agent behaviour |
|---|---|---|
| `clear` | No active alerts | Confirms all clear |
| `inform` | Minor advisory | Mentions if relevant |
| `watch` | Conditions possible | Notifies at next turn |
| `warning` | Take protective action | Interrupts conversation |
| `act_now` | Immediate life threat | Interrupts immediately |

## Getting started

### 1. Supabase schema

Run `apps/api/sql/schema.sql` in your Supabase SQL editor.

### 2. Environment variables

Copy and fill in `.env` for each app (both `apps/api/` and `apps/worker/` read `.env`):

```env
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENAI_API_KEY=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_WS_URL=
TWILIO_ACCOUNT_SID=        # optional
TWILIO_AUTH_TOKEN=         # optional
TWILIO_FROM_NUMBER=        # optional
OPENCLAW_GATEWAY_URL=      # optional
OPENCLAW_API_KEY=          # optional
```

### 3. Run the API

```bash
cd apps/api
pip install poetry && poetry install
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 4. Run the worker

```bash
cd apps/worker
poetry install
python -m src.main
```

Polls NWS every 5 minutes for states configured in `NWS_POLL_STATES` (default: `CA,TX,FL,NY`).

### 5. Seed demo data

```bash
cd apps/simulator
python scripts/seed_alerts.py --all
```

Seeds three realistic scenarios into Supabase for demo use.

### 6. Run the frontend

```bash
cd apps/web
npm install && npm run dev
```

## API overview

```
GET  /health
GET  /alerts/active         GET  /alerts/{id}
GET  /alerts/{id}/guidance
POST /voice/session          # mint OpenAI Realtime ephemeral token
POST /voice/tool-result      # dispatch tool call from browser data channel
POST /sessions               POST /sessions/{id}/attach-worker
POST /livekit/operator-token POST /livekit/worker-token
GET  /events/{session_id}    # SSE stream (agent status, approvals, screen events)
POST /places                 POST /contacts
POST /actions/call-contact   POST /actions/open-guidance
POST /actions/approve        POST /actions/deny
POST /workers/register       POST /workers/heartbeat
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — system diagram and design decisions
- [`docs/alert-lifecycle.md`](docs/alert-lifecycle.md) — 10-stage alert pipeline
- [`docs/voice-flow.md`](docs/voice-flow.md) — WebRTC sequence and tool dispatch flow

## License

MIT
