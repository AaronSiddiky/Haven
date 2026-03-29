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
      className="group relative flex flex-col items-center gap-5 focus:outline-none"
    >
      <div className="relative flex items-center justify-center">
        {/* Outer pulse ring */}
        <div
          className={`absolute h-44 w-44 rounded-full transition-all duration-700 ${
            state === "listening"
              ? "animate-pulse bg-[#a898c8]/15"
              : state === "speaking"
                ? "animate-pulse bg-[#d4a8b8]/20"
                : "bg-transparent"
          }`}
        />

        {/* Inner orb */}
        <div
          className={`relative z-10 flex h-32 w-32 items-center justify-center rounded-full transition-all duration-500 ${
            isError
              ? "border-2 border-red-400/60 bg-red-50/80 shadow-lg shadow-red-200/30"
              : isActive
                ? "border-2 border-[#a898c8]/50 bg-white/70 shadow-xl shadow-[#a898c8]/15 backdrop-blur-sm"
                : isThinking
                  ? "border-2 border-[#d4a8b8]/50 bg-white/70 shadow-lg shadow-[#d4a8b8]/15 backdrop-blur-sm"
                  : isConnecting
                    ? "border-2 border-fg/10 bg-white/50 backdrop-blur-sm"
                    : "border-2 border-black/[0.06] bg-white/60 shadow-sm backdrop-blur-sm hover:border-[#a898c8]/40 hover:bg-white/80 hover:shadow-md"
          }`}
        >
          {isThinking ? (
            <div className="flex gap-1.5">
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#d4a8b8] [animation-delay:0ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#bfb4d0] [animation-delay:150ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#a898c8] [animation-delay:300ms]" />
            </div>
          ) : isConnecting ? (
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-fg/10 border-t-fg/40" />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              className={`h-8 w-8 transition-colors duration-300 ${
                isError
                  ? "text-red-400"
                  : isActive
                    ? "text-[#8878a8]"
                    : "text-fg/30 group-hover:text-fg/55"
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
        className={`text-sm font-medium ${isError ? "text-red-500/70" : "text-fg/40"}`}
      >
        {STATE_LABEL[state]}
      </span>
    </button>
  );
}
