from fastapi import APIRouter, HTTPException

from app.schemas.worker import WorkerHeartbeatRequest, WorkerRegisterRequest
from app.services import status_event_service, worker_registry_service

router = APIRouter()


@router.post("/register", status_code=201)
def register_worker(body: WorkerRegisterRequest):
    return worker_registry_service.register(
        label=body.label,
        machine_name=body.machine_name,
        gateway_url=body.gateway_url,
        openclaw_mode=body.openclaw_mode,
    )


@router.post("/heartbeat")
def heartbeat(body: WorkerHeartbeatRequest):
    worker = worker_registry_service.get_worker(str(body.worker_id))
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker_registry_service.heartbeat(str(body.worker_id))


@router.post("/{worker_id}/screen-ready")
async def screen_ready(worker_id: str, session_id: str | None = None):
    worker = worker_registry_service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    updated = worker_registry_service.set_screen_ready(worker_id)

    if session_id:
        await status_event_service.screen_connected(session_id)

    return updated


@router.get("/{worker_id}")
def get_worker(worker_id: str):
    worker = worker_registry_service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker
