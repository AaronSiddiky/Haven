import { useEffect, useRef } from "react";
import type { TranscriptEntry } from "@/hooks/useVoiceSession";

interface TranscriptProps {
  entries: TranscriptEntry[];
}

export function Transcript({ entries }: TranscriptProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries.length]);

  if (entries.length === 0) {
    return (
      <div className="flex h-full items-center justify-center px-4 text-center">
        <p className="text-sm text-fg/35">
          Transcript will appear here as you speak.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 overflow-y-auto p-4">
      {entries.map((entry) => (
        <div
          key={entry.id}
          className={`flex flex-col gap-0.5 ${
            entry.role === "user" ? "items-end" : "items-start"
          }`}
        >
          <span className="text-[0.65rem] font-medium uppercase tracking-wider text-fg/30">
            {entry.role === "user" ? "You" : "Haven"}
          </span>
          <div
            className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
              entry.role === "user"
                ? "bg-[#a898c8]/10 text-fg"
                : "bg-white/50 text-fg"
            }`}
          >
            {entry.text}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
