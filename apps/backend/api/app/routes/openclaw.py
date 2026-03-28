from fastapi import APIRouter, HTTPException

from app.schemas.action import OpenClawCancelRequest, OpenClawExecuteRequest
from app.services import openclaw_service, session_service

router = APIRouter()


@router.post("/execute", status_code=202)
async def execute(body: OpenClawExecuteRequest):
    session = session_service.get_session(str(body.session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    gateway_url: str | None = None
    if session.get("worker_id"):
        from app.services import worker_registry_service
        worker = worker_registry_service.get_worker(session["worker_id"])
        if worker:
            gateway_url = worker.get("gateway_url")

    try:
        return await openclaw_service.execute(
            session_id=str(body.session_id),
            tool_name=body.tool_name,
            params=body.params,
            gateway_url=gateway_url,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenClaw error: {exc}")


@router.post("/cancel")
async def cancel(body: OpenClawCancelRequest):
    try:
        return await openclaw_service.cancel(body.run_id, session_id="")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenClaw cancel error: {exc}")


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    try:
        return await openclaw_service.get_run(run_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenClaw error: {exc}")
