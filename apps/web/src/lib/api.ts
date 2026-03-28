const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface VoiceSessionResponse {
  session_id: string;
  client_secret: string;
  model: string;
  expires_at: number;
}

export interface ToolCallResult {
  call_id: string;
  tool_name: string;
  result: Record<string, unknown>;
}

export interface LiveKitTokenData {
  token: string;
  ws_url: string;
  room_name: string;
  identity: string;
}

export interface HavenSession {
  id: string;
  status: string;
  livekit_room_name: string;
  worker_id: string | null;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API ${path} failed (${resp.status}): ${text}`);
  }
  return resp.json();
}

export async function createHavenSession(): Promise<HavenSession> {
  return post("/sessions", {});
}

export async function createVoiceSession(
  userId: string,
): Promise<VoiceSessionResponse> {
  return post("/voice/session", { user_id: userId });
}

export async function dispatchToolCall(
  toolName: string,
  args: Record<string, unknown>,
  callId: string,
): Promise<ToolCallResult> {
  return post("/voice/tool-result", {
    tool_name: toolName,
    arguments: args,
    call_id: callId,
  });
}

export async function getOperatorToken(
  sessionId: string,
): Promise<LiveKitTokenData> {
  return post("/livekit/operator-token", { session_id: sessionId });
}
