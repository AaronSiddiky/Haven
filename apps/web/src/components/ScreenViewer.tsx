import {
  LiveKitRoom,
  useTracks,
  VideoTrack,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface TokenData {
  token: string;
  ws_url: string;
  room_name: string;
  identity: string;
}

function RemoteScreen() {
  const tracks = useTracks([Track.Source.ScreenShare], {
    onlySubscribed: true,
  });

  const screenTrack = tracks.find(
    (t) => t.participant.identity === "haven-worker",
  );

  if (!screenTrack) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
        <div className="h-3 w-3 animate-pulse rounded-full bg-amber-400/60" />
        <p className="text-sm text-muted">Waiting for screen share...</p>
        <p className="text-xs text-muted/60">
          Open the share link on your machine to start streaming
        </p>
      </div>
    );
  }

  return (
    <VideoTrack
      trackRef={screenTrack}
      className="h-full w-full rounded-xl object-contain"
    />
  );
}

export function ScreenViewer() {
  const [tokenData, setTokenData] = useState<TokenData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_URL}/livekit/demo/viewer-token`)
      .then(async (resp) => {
        if (!resp.ok) throw new Error(`Token request failed: ${resp.status}`);
        return resp.json();
      })
      .then((data) => {
        if (!cancelled) setTokenData(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center px-4">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (!tokenData) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-muted border-t-transparent" />
          <p className="text-sm text-muted">Connecting to stream...</p>
        </div>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={tokenData.ws_url}
      token={tokenData.token}
      connect={true}
      className="h-full w-full"
    >
      <RemoteScreen />
    </LiveKitRoom>
  );
}
