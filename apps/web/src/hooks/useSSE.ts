import { useEffect, useRef, useState } from "react";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface SSEEvent {
  type: string;
  session_id: string;
  [key: string]: unknown;
}

export function useSSE(sessionId: string | null) {
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [connected, setConnected] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const es = new EventSource(`${BASE_URL}/events/${sessionId}`);
    sourceRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (e) => {
      try {
        const event: SSEEvent = JSON.parse(e.data);
        if (event.type === "ping") return;
        setLastEvent(event);
      } catch {
        /* ignore parse errors */
      }
    };

    es.onerror = () => {
      setConnected(false);
    };

    return () => {
      es.close();
      sourceRef.current = null;
      setConnected(false);
    };
  }, [sessionId]);

  return { lastEvent, connected };
}
