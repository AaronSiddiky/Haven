import { Link } from "react-router-dom";

/** Placeholder route so landing “Continue” has a target; full design comes next. */
export function VoiceCircle() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4">
      <p className="text-muted">Voice circle page — next step.</p>
      <Link
        to="/"
        className="mt-6 min-h-11 rounded-full border border-glass-border px-6 py-3 text-sm font-medium text-fg focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
      >
        Back home
      </Link>
    </div>
  );
}
