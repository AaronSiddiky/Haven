from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services import livekit_service, session_service

router = APIRouter()

DEMO_ROOM = "haven-demo"


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


@router.get("/demo/viewer-token")
def demo_viewer_token():
    """Subscriber token for the fixed demo room — no session needed."""
    return livekit_service.get_operator_token(DEMO_ROOM, "haven-viewer")


@router.get("/demo/publisher-token")
def demo_publisher_token():
    """Publisher token for the fixed demo room — used by the screen share page."""
    return livekit_service.get_worker_token(DEMO_ROOM, "haven-worker")
