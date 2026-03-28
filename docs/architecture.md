# Haven — Architecture

## System overview

Haven is a voice-first emergency alert assistant for people with disabilities. It monitors official alert feeds, explains active threats in plain language, and takes actions (opening guidance pages, contacting people) with user approval.

```
User (browser / voice)
        │
        ▼
┌──────────────────────────────────────────┐
│ Haven Web App (Next.js)                  │
│  Left pane  – transcript, agent status,  │
│               approvals, alert list       │
│  Right pane – live agent view (optional) │
└──────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  OpenAI Realtime        Haven API
  (voice + transcript)   (FastAPI)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
          Supabase         NWS API        OpenClaw
          (Postgres)    (alert feeds)  (browser actions)
              │
              ▼
          Worker
       (background jobs)
```

## Apps

### `apps/api/` — FastAPI backend

The control plane. Owns:
- Alert ingestion, normalization, classification
- Tool handler dispatch for voice agent
- User places, contacts, preferences
- Action logs and approvals
- OpenAI Realtime session minting
- OpenClaw orchestration

### `apps/worker/` — Background worker

Scheduled jobs:
- `poll_official_alerts` — NWS fetch every 5 minutes
- `expire_old_alerts` — mark ended alerts inactive
- `notify_users` — SMS for high-severity matches

### `apps/web/` — Next.js frontend

Accessible dashboard:
- Active alert list
- Voice interaction (microphone → OpenAI Realtime)
- Approval modals
- Contact and place management

### `apps/simulator/` — Demo scenarios

Seeded alert data for reliable hackathon demos:
- Flood warning (warning severity)
- Evacuation order (act_now severity, approval flow)
- Conflicting social signal (signal rejection demo)

## Packages

### `packages/shared-types/` — TypeScript contracts

Shared between frontend and any future TypeScript services:
- `NormalizedAlert`, `AlertSeverity`
- `ActionLog`, `ApprovalCard`
- `VoiceSessionConfig`, `TranscriptTurn`

### `packages/prompts/` — Agent prompt library

Versioned prompt files consumed by `openai_realtime_client.py`:
- `voice-agent.md` — system role and tool guidance
- `escalation.md` — severity tier response rules
- `summarization.md` — summary generation templates
- `safety.md` — non-negotiable safety rules

## Key design principles

1. **Backend does not relay media** — LiveKit handles screen-share, OpenAI handles audio
2. **Approvals before external actions** — calls, messages, browser actions always gated
3. **Official sources only** — social signals capped at `watch`, never amplified to `warning`+
4. **Three separated responsibilities** — alert intelligence / conversational intelligence / action execution
