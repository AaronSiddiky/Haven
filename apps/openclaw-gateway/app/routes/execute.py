"""
/execute — accepts a natural language instruction, forwards it to OpenClaw.
The gateway is a thin bridge. OpenClaw does all the work.
"""
import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.openclaw import send_message

logger = logging.getLogger(__name__)
router = APIRouter()

_runs: Dict[str, Dict[str, Any]] = {}


class ExecuteRequest(BaseModel):
    instruction: str
    session_id: str = ""


@router.post("/execute")
async def execute(body: ExecuteRequest):
    if not body.instruction.strip():
        raise HTTPException(status_code=400, detail="instruction is required")

    run_id = str(uuid.uuid4())
    _runs[run_id] = {"status": "running", "instruction": body.instruction}

    try:
        result = await send_message(body.instruction)
        _runs[run_id] = {"status": "completed", **result}
        logger.info("Task completed (run %s): %s", run_id, body.instruction[:80])
        return {"status": "ok", "run_id": run_id, **result}
    except Exception as exc:
        _runs[run_id] = {"status": "failed", "error": str(exc)}
        logger.error("Task failed (run %s): %s", run_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run_id": run_id, **run}


class CancelRequest(BaseModel):
    run_id: str


@router.post("/cancel")
def cancel_run(body: CancelRequest):
    run = _runs.get(body.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _runs[body.run_id]["status"] = "cancelled"
    return {"run_id": body.run_id, "status": "cancelled"}
