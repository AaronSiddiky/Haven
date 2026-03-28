import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ScreenViewer } from "@/components/ScreenViewer";
import { Transcript } from "@/components/Transcript";
import { VoiceOrb } from "@/components/VoiceOrb";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { useSSE } from "@/hooks/useSSE";
import { createHavenSession } from "@/lib/api";

const USER_ID = "demo-user";

export function VoiceCircle() {
  const [havenSessionId, setHavenSessionId] = useState<string | null>(null);
  const [showTranscript, setShowTranscript] = useState(true);
  const { state, transcript, error, connect, disconnect } =
    useVoiceSession(USER_ID);
  const { lastEvent } = useSSE(havenSessionId);
  const [screenReady, setScreenReady] = useState(false);

  useEffect(() => {
    createHavenSession()
      .then((s) => setHavenSessionId(s.id))
      .catch((err) => console.error("Failed to create Haven session:", err));
  }, []);

  useEffect(() => {
    if (lastEvent?.type === "screen.connected") {
      setScreenReady(true);
    }
  }, [lastEvent]);

  const handleOrbClick = () => {
    if (state === "idle" || state === "error") {
      connect();
    } else {
      disconnect();
    }
  };

  const isConnected =
    state !== "idle" && state !== "connecting" && state !== "error";

  return (
    <div className="flex h-screen flex-col bg-canvas">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-glass-border px-4 py-3 sm:px-6">
        <Link
          to="/"
          className="flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-fg"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="h-4 w-4"
          >
            <path
              fillRule="evenodd"
              d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z"
              clipRule="evenodd"
            />
          </svg>
          Back
        </Link>

        <div className="flex items-center gap-3">
          {error && (
            <span className="text-xs text-red-400" role="alert">
              {error}
            </span>
          )}
          <div className="flex items-center gap-1.5">
            <div
              className={`h-2 w-2 rounded-full ${
                isConnected ? "bg-green-400" : "bg-muted/40"
              }`}
            />
            <span className="text-xs font-medium text-muted">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left pane — Voice */}
        <div className="flex flex-1 flex-col items-center justify-center">
          <VoiceOrb state={state} onClick={handleOrbClick} />
        </div>

        {/* Right pane — Screen viewer */}
        <div className="hidden w-1/2 border-l border-glass-border bg-black/5 lg:block">
          {havenSessionId ? (
            screenReady ? (
              <ScreenViewer sessionId={havenSessionId} />
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
                <div className="rounded-xl border border-glass-border bg-glass px-5 py-4">
                  <p className="text-sm font-medium text-fg">
                    Screen share not connected
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    Open the screen share page on your machine to see OpenClaw
                    in action.
                  </p>
                </div>
              </div>
            )
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-muted border-t-transparent" />
            </div>
          )}
        </div>
      </div>

      {/* Bottom — Transcript */}
      <div
        className={`border-t border-glass-border transition-all duration-300 ${
          showTranscript ? "h-56" : "h-10"
        }`}
      >
        <button
          onClick={() => setShowTranscript(!showTranscript)}
          className="flex w-full items-center justify-between px-4 py-2.5 text-xs font-medium text-muted hover:text-fg"
        >
          <span>Transcript</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className={`h-4 w-4 transition-transform ${showTranscript ? "rotate-180" : ""}`}
          >
            <path
              fillRule="evenodd"
              d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
              clipRule="evenodd"
            />
          </svg>
        </button>
        {showTranscript && (
          <div className="h-[calc(100%-2.5rem)] overflow-hidden">
            <Transcript entries={transcript} />
          </div>
        )}
      </div>
    </div>
  );
}
