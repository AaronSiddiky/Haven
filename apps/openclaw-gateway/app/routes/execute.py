import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.tools import click, execute_task, open_url, search, take_screenshot, type_text

logger = logging.getLogger(__name__)
router = APIRouter()

TOOL_MAP = {
    "open_url": open_url.handle,
    "search": search.handle,
    "click": click.handle,
    "type": type_text.handle,
    "screenshot": take_screenshot.handle,
    "execute_task": execute_task.handle,
}

_runs: Dict[str, Dict[str, Any]] = {}


class ExecuteRequest(BaseModel):
    tool: str
    params: Dict[str, Any] = {}


@router.post("/execute")
async def execute(body: ExecuteRequest):
    handler = TOOL_MAP.get(body.tool)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {body.tool}")

    run_id = str(uuid.uuid4())
    _runs[run_id] = {"status": "running", "tool": body.tool}

    try:
        result = await handler(body.params, run_id)
        _runs[run_id] = {"status": "completed", "tool": body.tool, "result": result}
        logger.info("Tool '%s' completed (run %s)", body.tool, run_id)
        return {"status": "ok", "run_id": run_id, **result}
    except Exception as exc:
        _runs[run_id] = {"status": "failed", "tool": body.tool, "error": str(exc)}
        logger.error("Tool '%s' failed (run %s): %s", body.tool, run_id, exc)
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
