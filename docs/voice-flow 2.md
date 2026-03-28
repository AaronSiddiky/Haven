# Voice Flow — Haven

## Connection sequence

```
Browser                  Haven API              OpenAI Realtime
   │                         │                        │
   │  POST /voice/session     │                        │
   │─────────────────────────▶│                        │
   │                         │  POST /v1/realtime/sessions
   │                         │───────────────────────▶│
   │                         │◀───────────────────────│
   │                         │  { id, client_secret } │
   │◀─────────────────────────│                        │
   │  { session_id,           │                        │
   │    client_secret }       │                        │
   │                         │                        │
   │  RTCPeerConnection (WebRTC)                       │
   │◀────────────────────────────────────────────────▶│
   │  microphone in / audio out / data channel         │
```

## Turn sequence (voice → tool → response)

```
User speaks
    │
    ▼
OpenAI VAD detects end of turn
    │
    ▼
OpenAI transcribes + processes
    │
    ├─ Simple response ──────────────────────────────▶ TTS plays in browser
    │
    └─ Tool call decided
            │
            ▼
        Browser receives tool_call event on data channel
            │
            ▼
        POST /voice/tool-result { tool_name, arguments, call_id }
            │
            ▼
        Haven API dispatches to tool_handlers/{tool_name}.py
            │
            ├─ No approval needed ────────────────────▶ result returned
            │
            └─ Approval required
                    │
                    ▼
                Backend creates action_log (requires_approval=true)
                    │
                    ▼
                Returns { status: "approval_required", action_id }
                    │
                    ▼
                Browser shows ApprovalModal
                    │
                    ├─ User approves → POST /actions/approve
                    │       │
                    │       ▼
                    │   Tool executes, result returned to OpenAI
                    │
                    └─ User denies → POST /actions/deny
                            │
                            ▼
                        Cancelled, assistant informed
            │
            ▼
        Browser sends tool_result back to OpenAI via data channel
            │
            ▼
        OpenAI generates spoken response from result
            │
            ▼
        TTS audio plays in browser
```

## Interruption handling

OpenAI Realtime uses server-side VAD (Voice Activity Detection). When the user speaks while the assistant is talking:
1. The data channel receives a `input_audio_buffer.speech_started` event
2. The browser cancels the current audio playback
3. OpenAI processes the new input immediately

Haven's frontend should:
- Listen for `response.audio.delta` to show "speaking" state
- Listen for `input_audio_buffer.speech_started` to show "listening" state
- Transition smoothly between states without requiring user button presses

## Reconnection

If the WebRTC connection drops:
1. Browser detects `connectionState === 'disconnected'`
2. Call `POST /voice/session` again to get a new ephemeral token
3. Re-establish RTCPeerConnection
4. Reload recent transcript from `GET /voice/transcript/{session_id}`

The Haven session remains alive on the backend — only the WebRTC channel reconnects.

## Data channel event types (OpenAI → Browser)

| Event type | Meaning |
|---|---|
| `session.created` | Session ready |
| `conversation.item.created` | New transcript turn |
| `response.audio.delta` | Audio chunk streaming |
| `response.done` | Response complete |
| `response.function_call_arguments.done` | Tool call ready to dispatch |
| `input_audio_buffer.speech_started` | User started speaking |
| `input_audio_buffer.speech_stopped` | User stopped speaking |
| `error` | Session error |
