from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services import livekit_service, session_service

router = APIRouter()


class TokenRequest(BaseModel):
    session_id: str
    identity: Optional[str] = None


@router.post("/operator-token")
def operator_token(body: TokenRequest):
    session = session_service.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return livekit_service.get_operator_token(session["livekit_room_name"], body.identity or "haven-operator")


@router.post("/worker-token")
def worker_token(body: TokenRequest):
    session = session_service.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return livekit_service.get_worker_token(session["livekit_room_name"], body.identity or "haven-worker")
