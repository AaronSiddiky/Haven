import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ScreenViewer } from "@/components/ScreenViewer";
import { Transcript } from "@/components/Transcript";
import { VoiceOrb } from "@/components/VoiceOrb";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { useSSE } from "@/hooks/useSSE";
import { createHavenSession } from "@/lib/api";

const USER_ID = "demo-user";

export function VoiceCircle() {
  const { state, transcript, error, connect, disconnect, injectMessage } =
    useVoiceSession(USER_ID);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const { lastEvent } = useSSE(sessionId);
  const lastAlertRef = useRef<string | null>(null);

  useEffect(() => {
    createHavenSession()
      .then((s) => setSessionId(s.id))
      .catch((err) => console.error("Failed to create Haven session:", err));
  }, []);

  useEffect(() => {
    if (!lastEvent || lastEvent.type !== "watchtower.alert") return;
    const content = lastEvent.content as string;
    const sourceUser = lastEvent.source_user as string;
    const summary = lastEvent.summary as string;

    const alertKey = `${sourceUser}:${content?.slice(0, 40)}`;
    if (alertKey === lastAlertRef.current) return;
    lastAlertRef.current = alertKey;

    const alertText =
      `URGENT ALERT: @${sourceUser} just posted: "${content}". ` +
      `Summary: ${summary}. ` +
      `This is a geopolitical emergency. Announce this to me immediately, ` +
      `then turn on the light and buy a Mini Outdoor First Aid Kit for $0.95 from Amazon.`;

    injectMessage(alertText);
  }, [lastEvent, injectMessage]);

  const handleOrbClick = () => {
    if (state === "idle" || state === "error") {
      connect();
    } else {
      disconnect();
    }
  };

  const isConnected =
    state !== "idle" && state !== "connecting" && state !== "error";
  const isVoiceActive = state === "listening" || state === "speaking";
  const isThinking = state === "thinking";

  return (
    <div className="relative flex h-[100dvh] flex-col overflow-hidden bg-[#f6f4fb]">

      {/* Header */}
      <header className="relative z-20 h-14">
        <Link
          to="/"
          className="absolute left-4 top-3 inline-flex w-auto items-center rounded-lg py-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue sm:left-6"
        >
          <span className="relative block h-10 w-[138px] overflow-hidden">
            <img
              src="/Haven Logo.png"
              alt="Haven"
              className="absolute inset-0 h-full w-full scale-[2.6] object-contain"
            />
          </span>
        </Link>

        <div className="absolute right-4 top-3 flex items-center gap-3 sm:right-6">
          {error && (
            <span className="text-xs text-red-500/80" role="alert">
              {error}
            </span>
          )}
          <div className="flex items-center gap-2 rounded-full border border-black/10 bg-white px-3 py-1.5 shadow-sm">
            <div
              className={`h-1.5 w-1.5 rounded-full transition-colors duration-500 ${
                isConnected ? "bg-emerald-500" : "bg-fg/20"
              }`}
            />
            <span className="text-xs font-medium text-fg/60">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>
      </header>

      {/* Main content: separate rounded panes */}
      <div className="relative z-10 grid min-h-0 flex-1 grid-cols-1 gap-4 overflow-hidden px-3 sm:px-5 lg:grid-cols-2 lg:gap-5 lg:px-6">
        {/* Left pane — Screen share */}
        <div className="min-h-0 overflow-hidden rounded-3xl border border-black/10 bg-white shadow-[0_3px_14px_rgba(20,20,40,0.05)]">
          <div className="flex h-12 items-center justify-between border-b border-black/5 px-4">
            <span className="text-xs font-semibold uppercase tracking-[0.15em] text-fg/45">
              Screen share
            </span>
            <span className="rounded-full bg-[#f7f7fb] px-2.5 py-1 text-[0.65rem] font-medium text-fg/45">
              Live
            </span>
          </div>
          <div className="h-[calc(100%-3rem)] p-2">
            <div className="h-full overflow-hidden rounded-2xl border border-black/[0.06] bg-white">
              <ScreenViewer />
            </div>
          </div>
        </div>

        {/* Right pane — Transcript rectangle */}
        <div className="min-h-0 overflow-hidden rounded-3xl border border-black/10 bg-white shadow-[0_3px_14px_rgba(20,20,40,0.05)]">
          <div className="flex h-12 items-center justify-between border-b border-black/5 px-4">
            <span className="text-xs font-semibold uppercase tracking-[0.15em] text-fg/45">
              Transcript
            </span>
            <span className="text-[0.7rem] text-fg/35">
              {transcript.length} message{transcript.length === 1 ? "" : "s"}
            </span>
          </div>
          <div className="h-[calc(100%-3rem)] overflow-hidden">
            <Transcript entries={transcript} />
          </div>
        </div>
      </div>

      {/* Bottom center — Voice controls + reactive visualizer */}
      <div className="relative z-20 px-3 pb-4 pt-4 sm:px-5 lg:px-6">
        <div className="mx-auto w-full max-w-[430px] rounded-3xl border border-black/10 bg-white p-4 shadow-[0_3px_14px_rgba(20,20,40,0.05)]">
          <div className="flex items-center justify-center gap-2.5 pb-3">
            {[0, 1, 2, 3, 4, 5, 6].map((i) => (
              <span
                key={i}
                className={`w-1.5 rounded-full transition-all duration-500 ${
                  isVoiceActive
                    ? "h-6 animate-pulse bg-[#9178c2]/75"
                    : isThinking
                      ? "h-4 animate-pulse bg-[#6fa6de]/70"
                      : "h-2 bg-fg/18"
                }`}
                style={{
                  animationDelay: `${i * 90}ms`,
                  height: isVoiceActive ? `${18 + ((i % 3) + 1) * 6}px` : undefined,
                }}
              />
            ))}
          </div>
          <div className="flex items-center justify-center">
            <VoiceOrb state={state} onClick={handleOrbClick} />
          </div>
        </div>
      </div>
    </div>
  );
}
