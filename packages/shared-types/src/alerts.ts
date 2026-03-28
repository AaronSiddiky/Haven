export type AlertSeverity = "clear" | "inform" | "watch" | "warning" | "act_now";

export const SEVERITY_ORDER: AlertSeverity[] = [
  "clear",
  "inform",
  "watch",
  "warning",
  "act_now",
];

export function severityIndex(s: AlertSeverity): number {
  return SEVERITY_ORDER.indexOf(s);
}

export function isAtLeast(a: AlertSeverity, b: AlertSeverity): boolean {
  return severityIndex(a) >= severityIndex(b);
}

export interface AlertSource {
  id: string;
  name: string;
  url?: string;
  timestamp: string;
  official: boolean;
}

export interface NormalizedAlert {
  id: string;
  raw_alert_id?: string;
  headline: string;
  location_label: string;
  hazard_type: string;
  severity: AlertSeverity;
  starts_at?: string;
  ends_at?: string;
  summary: string;
  description: string;
  instruction?: string;
  recommended_actions: string[];
  source: AlertSource;
  is_active: boolean;
  fetched_at: string;
  geometry?: import("geojson").Geometry | null;
}

export interface AlertSummary
  extends Pick<
    NormalizedAlert,
    | "id"
    | "headline"
    | "location_label"
    | "hazard_type"
    | "severity"
    | "starts_at"
    | "ends_at"
    | "summary"
    | "is_active"
  > {}

export interface AlertsResponse {
  count: number;
  alerts: NormalizedAlert[];
}
