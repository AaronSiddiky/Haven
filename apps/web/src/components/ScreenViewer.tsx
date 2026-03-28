import {
  LiveKitRoom,
  useTracks,
  VideoTrack,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState } from "react";
import { getOperatorToken, type LiveKitTokenData } from "@/lib/api";

interface ScreenViewerProps {
  sessionId: string;
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
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-muted">Waiting for screen share...</p>
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

export function ScreenViewer({ sessionId }: ScreenViewerProps) {
  const [tokenData, setTokenData] = useState<LiveKitTokenData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getOperatorToken(sessionId)
      .then((data) => {
        if (!cancelled) setTokenData(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

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
