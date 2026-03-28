from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.services import session_service, status_event_service

router = APIRouter()


class AttachWorkerRequest(BaseModel):
    worker_id: UUID


@router.post("", status_code=201)
async def create_session():
    session = session_service.create_session()
    await status_event_service.session_ready(session["id"], session["livekit_room_name"])
    return session


@router.get("/{session_id}")
def get_session(session_id: str):
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/attach-worker")
async def attach_worker(session_id: str, body: AttachWorkerRequest):
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    updated = session_service.attach_worker(session_id, str(body.worker_id))
    await status_event_service.worker_connected(session_id, str(body.worker_id))
    return updated


@router.post("/{session_id}/end")
def end_session(session_id: str):
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_service.end_session(session_id)
