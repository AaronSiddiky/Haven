-- Haven DB schema for Supabase (PostgreSQL)
-- Run this in the Supabase SQL editor to set up all tables.

create extension if not exists "uuid-ossp";

-- ─── Workers ──────────────────────────────────────────────────────────────────
create table if not exists workers (
    id                  uuid primary key default uuid_generate_v4(),
    label               text not null,
    machine_name        text not null,
    gateway_url         text not null,
    status              text not null default 'offline'
                            check (status in ('offline', 'idle', 'active')),
    last_seen_at        timestamptz,
    openclaw_mode       text not null default 'openclaw'
                            check (openclaw_mode in ('openclaw', 'user')),
    screen_stream_status text not null default 'disconnected'
                            check (screen_stream_status in ('disconnected', 'connected')),
    created_at          timestamptz not null default now()
);

-- ─── Sessions ─────────────────────────────────────────────────────────────────
create table if not exists sessions (
    id                  uuid primary key default uuid_generate_v4(),
    status              text not null default 'pending'
                            check (status in ('pending', 'active', 'ended', 'error')),
    livekit_room_name   text not null,
    openai_session_id   text,
    worker_id           uuid references workers(id),
    created_at          timestamptz not null default now(),
    ended_at            timestamptz
);

-- ─── Approvals ────────────────────────────────────────────────────────────────
create table if not exists approvals (
    id              uuid primary key default uuid_generate_v4(),
    session_id      uuid not null references sessions(id) on delete cascade,
    action_type     text not null,
    payload_json    jsonb not null default '{}',
    status          text not null default 'pending'
                        check (status in ('pending', 'approved', 'denied', 'expired')),
    requested_at    timestamptz not null default now(),
    resolved_at     timestamptz
);

-- ─── Transcript turns ─────────────────────────────────────────────────────────
create table if not exists transcript_turns (
    id          uuid primary key default uuid_generate_v4(),
    session_id  uuid not null references sessions(id) on delete cascade,
    speaker     text not null check (speaker in ('user', 'assistant')),
    text        text not null,
    timestamp   timestamptz not null default now()
);

-- ─── Action logs ──────────────────────────────────────────────────────────────
create table if not exists action_logs (
    id              uuid primary key default uuid_generate_v4(),
    session_id      uuid not null references sessions(id) on delete cascade,
    tool_name       text not null,
    status          text not null default 'pending'
                        check (status in ('pending', 'running', 'completed', 'failed')),
    message         text,
    metadata_json   jsonb default '{}',
    created_at      timestamptz not null default now()
);

-- ─── Worker events ────────────────────────────────────────────────────────────
create table if not exists worker_events (
    id              uuid primary key default uuid_generate_v4(),
    worker_id       uuid not null references workers(id) on delete cascade,
    session_id      uuid references sessions(id) on delete cascade,
    event_type      text not null,
    payload_json    jsonb default '{}',
    created_at      timestamptz not null default now()
);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
create index if not exists idx_sessions_worker_id     on sessions(worker_id);
create index if not exists idx_sessions_status        on sessions(status);
create index if not exists idx_approvals_session_id   on approvals(session_id);
create index if not exists idx_approvals_status       on approvals(status);
create index if not exists idx_transcript_session_id  on transcript_turns(session_id);
create index if not exists idx_action_logs_session_id on action_logs(session_id);
create index if not exists idx_worker_events_worker   on worker_events(worker_id);
