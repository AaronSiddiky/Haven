import type { VoiceState } from "@/hooks/useVoiceSession";

const STATE_LABEL: Record<VoiceState, string> = {
  idle: "Tap to connect",
  connecting: "Connecting...",
  connected: "Ready — start speaking",
  listening: "Listening...",
  speaking: "Speaking...",
  thinking: "Thinking...",
  error: "Connection error",
};

interface VoiceOrbProps {
  state: VoiceState;
  onClick: () => void;
}

export function VoiceOrb({ state, onClick }: VoiceOrbProps) {
  const isActive = state === "listening" || state === "speaking";
  const isThinking = state === "thinking";
  const isError = state === "error";
  const isConnecting = state === "connecting";

  return (
    <button
      onClick={onClick}
      aria-label={STATE_LABEL[state]}
      className="group relative flex flex-col items-center gap-4 focus:outline-none"
    >
      <div className="relative flex items-center justify-center">
        {/* Outer pulse ring */}
        <div
          className={`absolute h-40 w-40 rounded-full transition-all duration-700 ${
            state === "listening"
              ? "animate-pulse bg-accent-blue/15"
              : state === "speaking"
                ? "animate-pulse bg-accent-orange/15"
                : "bg-transparent"
          }`}
        />

        {/* Inner orb */}
        <div
          className={`relative z-10 flex h-28 w-28 items-center justify-center rounded-full border-2 transition-all duration-300 ${
            isError
              ? "border-red-400 bg-red-500/10"
              : isActive
                ? "border-accent-blue bg-accent-blue/10 shadow-lg shadow-accent-blue/20"
                : isThinking
                  ? "border-accent-orange bg-accent-orange/10"
                  : isConnecting
                    ? "border-muted bg-muted/10"
                    : "border-glass-border bg-glass hover:border-accent-blue/50 hover:bg-accent-blue/5"
          }`}
        >
          {/* Center icon */}
          {isThinking ? (
            <div className="flex gap-1.5">
              <span className="h-2 w-2 animate-bounce rounded-full bg-accent-orange [animation-delay:0ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-accent-orange [animation-delay:150ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-accent-orange [animation-delay:300ms]" />
            </div>
          ) : isConnecting ? (
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted border-t-transparent" />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              className={`h-8 w-8 transition-colors ${
                isError
                  ? "text-red-400"
                  : isActive
                    ? "text-accent-blue"
                    : "text-muted group-hover:text-fg"
              }`}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
              />
            </svg>
          )}
        </div>
      </div>

      <span
        className={`text-sm font-medium ${isError ? "text-red-400" : "text-muted"}`}
      >
        {STATE_LABEL[state]}
      </span>
    </button>
  );
}
