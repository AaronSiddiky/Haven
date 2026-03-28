-- Haven API DB schema for Supabase (PostgreSQL)
-- Run this in the Supabase SQL editor.

create extension if not exists "uuid-ossp";

-- ─── Users (minimal — auth via Supabase Auth) ────────────────────────────────
create table if not exists monitored_places (
    id              uuid primary key default uuid_generate_v4(),
    user_id         text not null,
    label           text not null,
    address         text,
    lat             double precision not null,
    lon             double precision not null,
    radius_km       double precision not null default 25.0,
    notify_on_watch  boolean not null default true,
    notify_on_warning boolean not null default true,
    created_at      timestamptz not null default now()
);

create table if not exists emergency_contacts (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             text not null,
    name                text not null,
    phone               text not null,
    relationship        text,
    notify_automatically boolean not null default false,
    created_at          timestamptz not null default now()
);

create table if not exists user_preferences (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             text not null unique,
    minimum_severity    text not null default 'watch'
                            check (minimum_severity in ('inform', 'watch', 'warning', 'act_now')),
    voice_interruptions boolean not null default true,
    sms_notifications   boolean not null default false,
    hazard_types_filter jsonb not null default '[]',
    updated_at          timestamptz not null default now()
);

-- ─── Alerts ───────────────────────────────────────────────────────────────────
create table if not exists raw_alerts (
    id              uuid primary key default uuid_generate_v4(),
    source_name     text not null,
    external_id     text not null,
    payload_json    jsonb not null default '{}',
    fetched_at      timestamptz not null default now(),
    processed       boolean not null default false,
    unique (source_name, external_id)
);

create table if not exists normalized_alerts (
    id                  uuid primary key default uuid_generate_v4(),
    raw_alert_id        uuid references raw_alerts(id),
    headline            text not null,
    location_label      text not null,
    hazard_type         text not null,
    severity            text not null
                            check (severity in ('clear', 'inform', 'watch', 'warning', 'act_now')),
    starts_at           timestamptz,
    ends_at             timestamptz,
    summary             text not null,
    description         text not null default '',
    instruction         text,
    recommended_actions jsonb not null default '[]',
    source              jsonb not null default '{}',
    is_active           boolean not null default true,
    fetched_at          timestamptz not null default now(),
    geometry            jsonb
);

-- ─── Action logs ──────────────────────────────────────────────────────────────
create table if not exists action_logs (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             text not null,
    action_type         text not null,
    status              text not null default 'pending'
                            check (status in ('pending', 'approved', 'denied', 'running', 'completed', 'failed')),
    payload_json        jsonb default '{}',
    result_json         jsonb,
    requires_approval   boolean not null default false,
    approved            boolean,
    created_at          timestamptz not null default now()
);

-- ─── Sessions (LiveKit room management) ──────────────────────────────────────
create table if not exists sessions (
    id                  uuid primary key default uuid_generate_v4(),
    status              text not null default 'pending'
                            check (status in ('pending', 'active', 'ended')),
    livekit_room_name   text not null,
    openai_session_id   text,
    worker_id           uuid,
    created_at          timestamptz not null default now(),
    ended_at            timestamptz
);

-- ─── Workers (OpenClaw host + screen-share publisher) ─────────────────────────
create table if not exists workers (
    id                  uuid primary key default uuid_generate_v4(),
    label               text not null,
    machine_name        text not null,
    gateway_url         text not null,
    openclaw_mode       text not null default 'openclaw',
    status              text not null default 'idle'
                            check (status in ('idle', 'active', 'offline')),
    screen_stream_status text not null default 'disconnected'
                            check (screen_stream_status in ('disconnected', 'connected')),
    last_seen_at        timestamptz,
    created_at          timestamptz not null default now()
);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
create index if not exists idx_monitored_places_user      on monitored_places(user_id);
create index if not exists idx_emergency_contacts_user    on emergency_contacts(user_id);
create index if not exists idx_normalized_alerts_active   on normalized_alerts(is_active, fetched_at desc);
create index if not exists idx_normalized_alerts_severity on normalized_alerts(severity);
create index if not exists idx_action_logs_user           on action_logs(user_id, created_at desc);
create index if not exists idx_raw_alerts_source          on raw_alerts(source_name, external_id);
