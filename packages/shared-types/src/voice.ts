export type VoiceSessionStatus =
  | "idle"
  | "connecting"
  | "listening"
  | "thinking"
  | "speaking"
  | "tool_calling"
  | "awaiting_approval"
  | "error"
  | "disconnected";

export interface TranscriptTurn {
  id?: string;
  speaker: "user" | "assistant";
  text: string;
  timestamp: string;
  tool_call?: ToolCallSummary;
}

export interface ToolCallSummary {
  tool_name: string;
  status: "started" | "completed" | "failed";
  label: string;
}

export interface VoiceSessionConfig {
  session_id: string;
  client_secret: string;
  model: string;
  expires_at?: string;
}

export interface ToolCallEvent {
  type: "tool_call";
  call_id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResultEvent {
  type: "tool_result";
  call_id: string;
  tool_name: string;
  result: unknown;
}
