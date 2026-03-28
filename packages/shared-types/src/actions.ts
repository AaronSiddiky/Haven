export type ActionStatus =
  | "pending"
  | "approved"
  | "denied"
  | "running"
  | "completed"
  | "failed";

export type ActionType =
  | "call_contact"
  | "open_guidance"
  | "open_evacuation_page"
  | "search_transport"
  | "approve"
  | "deny";

export interface ActionLog {
  id: string;
  user_id: string;
  action_type: ActionType;
  status: ActionStatus;
  payload_json?: Record<string, unknown>;
  result_json?: Record<string, unknown>;
  requires_approval: boolean;
  approved?: boolean;
  created_at: string;
}

export interface ApprovalCard {
  action_id: string;
  action_type: ActionType;
  label: string;
  description: string;
  requires_approval: true;
}

export interface CallContactPayload {
  contact_id: string;
  message?: string;
  alert_id?: string;
}

export interface OpenGuidancePayload {
  alert_id: string;
  session_id?: string;
}
