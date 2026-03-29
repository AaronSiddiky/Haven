import { useCallback, useEffect, useRef, useState } from "react";
import { createVoiceSession, dispatchToolCall } from "@/lib/api";

export type VoiceState =
  | "idle"
  | "connecting"
  | "connected"
  | "listening"
  | "speaking"
  | "thinking"
  | "error";

export interface TranscriptEntry {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: number;
}

interface UseVoiceSessionReturn {
  state: VoiceState;
  transcript: TranscriptEntry[];
  error: string | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  injectMessage: (text: string) => void;
}

const OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime";

export function useVoiceSession(userId: string): UseVoiceSessionReturn {
  const [state, setState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sessionIdRef = useRef<string>("");
  const entryIdRef = useRef(0);

  const addTranscript = useCallback(
    (role: "user" | "assistant", text: string) => {
      setTranscript((prev) => [
        ...prev,
        {
          id: String(++entryIdRef.current),
          role,
          text,
          timestamp: Date.now(),
        },
      ]);
    },
    [],
  );

  const pendingInjectionRef = useRef<string | null>(null);

  const injectMessage = useCallback((text: string) => {
    const dc = dcRef.current;
    if (!dc || dc.readyState !== "open") return;

    pendingInjectionRef.current = text;

    dc.send(JSON.stringify({ type: "response.cancel" }));

    setTimeout(() => {
      if (!pendingInjectionRef.current) return;
      const msg = pendingInjectionRef.current;
      pendingInjectionRef.current = null;
      const channel = dcRef.current;
      if (!channel || channel.readyState !== "open") return;

      channel.send(
        JSON.stringify({
          type: "conversation.item.create",
          item: {
            type: "message",
            role: "user",
            content: [{ type: "input_text", text: msg }],
          },
        }),
      );
      channel.send(JSON.stringify({ type: "response.create" }));
    }, 500);
  }, []);

  const disconnect = useCallback(() => {
    dcRef.current?.close();
    pcRef.current?.close();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    pcRef.current = null;
    dcRef.current = null;
    streamRef.current = null;
    setState("idle");
  }, []);

  const connect = useCallback(async () => {
    if (pcRef.current) disconnect();

    setState("connecting");
    setError(null);
    setTranscript([]);

    try {
      const session = await createVoiceSession(userId);
      sessionIdRef.current = session.session_id;
      const model = session.model;
      const clientSecret = session.client_secret;

      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      const audio = new Audio();
      audio.autoplay = true;
      audioRef.current = audio;
      pc.ontrack = (e) => {
        audio.srcObject = e.streams[0];
      };

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));

      const dc = pc.createDataChannel("oai-events");
      dcRef.current = dc;

      dc.onopen = () => {
        setState("connected");
      };

      dc.onmessage = async (e) => {
        const event = JSON.parse(e.data);

        switch (event.type) {
          case "session.created":
          case "session.updated":
            setState("connected");
            break;

          case "input_audio_buffer.speech_started":
            setState("listening");
            break;

          case "input_audio_buffer.speech_stopped":
            setState("thinking");
            break;

          case "response.audio.delta":
            setState("speaking");
            break;

          case "response.done":
            setState("connected");
            break;

          case "conversation.item.input_audio_transcription.completed":
            if (event.transcript) {
              addTranscript("user", event.transcript);
            }
            break;

          case "response.audio_transcript.done":
            if (event.transcript) {
              addTranscript("assistant", event.transcript);
            }
            break;

          case "response.function_call_arguments.done": {
            setState("thinking");
            const toolName: string = event.name;
            const rawArgs: string = event.arguments;
            const callId: string = event.call_id;

            let args: Record<string, unknown> = {};
            try {
              args = JSON.parse(rawArgs);
            } catch {
              args = {};
            }

            args.session_id = sessionIdRef.current;

            try {
              const result = await dispatchToolCall(toolName, args, callId);

              dc.send(
                JSON.stringify({
                  type: "conversation.item.create",
                  item: {
                    type: "function_call_output",
                    call_id: callId,
                    output: JSON.stringify(result.result),
                  },
                }),
              );
              dc.send(JSON.stringify({ type: "response.create" }));
            } catch (err) {
              dc.send(
                JSON.stringify({
                  type: "conversation.item.create",
                  item: {
                    type: "function_call_output",
                    call_id: callId,
                    output: JSON.stringify({
                      error: String(err),
                    }),
                  },
                }),
              );
              dc.send(JSON.stringify({ type: "response.create" }));
            }
            break;
          }

          case "error": {
            const msg = event.error?.message ?? "Unknown realtime error";
            if (msg.includes("cancel") || msg.includes("interrupted")) {
              break;
            }
            setError(msg);
            setState("error");
            break;
          }
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const sdpResp = await fetch(`${OPENAI_REALTIME_URL}?model=${model}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${clientSecret}`,
          "Content-Type": "application/sdp",
        },
        body: offer.sdp,
      });

      if (!sdpResp.ok) {
        throw new Error(
          `OpenAI SDP exchange failed (${sdpResp.status}): ${await sdpResp.text()}`,
        );
      }

      const answerSdp = await sdpResp.text();
      await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });

      pc.oniceconnectionstatechange = () => {
        if (
          pc.iceConnectionState === "disconnected" ||
          pc.iceConnectionState === "failed"
        ) {
          setError("WebRTC connection lost");
          setState("error");
        }
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      setState("error");
    }
  }, [userId, disconnect, addTranscript]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { state, transcript, error, connect, disconnect, injectMessage };
}
