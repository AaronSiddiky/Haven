from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services import openai_realtime_service, transcript_service

router = APIRouter()


class RealtimeSessionRequest(BaseModel):
    session_id: str


class TranscriptTurnRequest(BaseModel):
    session_id: str
    speaker: str
    text: str


@router.post("/realtime-session")
async def realtime_session(body: RealtimeSessionRequest):
    """
    Mint an OpenAI Realtime ephemeral token for the browser WebRTC client.

    The browser uses response.client_secret.value to connect directly
    to the OpenAI Realtime API – the backend does not relay audio.
    """
    try:
        result = await openai_realtime_service.mint_ephemeral_token(body.session_id)
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI Realtime error: {exc}")


@router.post("/transcript")
def add_transcript_turn(body: TranscriptTurnRequest):
    """Persist a transcript turn from the browser."""
    return transcript_service.add_turn(body.session_id, body.speaker, body.text)


@router.get("/transcript/{session_id}")
def get_transcript(session_id: str):
    return transcript_service.get_turns(session_id)
