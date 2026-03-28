"""
OpenClaw orchestration layer.

Dispatches browser tasks to the remote OpenClaw gateway, tracks
run state in action_logs, and emits status events to the frontend.
"""
import logging
import uuid
from typing import Any, Dict, Optional

from app.db.client import get_supabase
from app.integrations import openclaw_gateway_client
from app.services import status_event_service

logger = logging.getLogger(__name__)

TABLE = "action_logs"


def _log_action(session_id: str, tool_name: str, status: str, message: str = "", metadata: dict = {}) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "tool_name": tool_name,
        "status": status,
        "message": message,
        "metadata_json": metadata,
    }
    get_supabase().table(TABLE).insert(row).execute()
    return row


def _update_log(log_id: str, status: str, message: str = "", metadata: dict = {}) -> None:
    get_supabase().table(TABLE).update(
        {"status": status, "message": message, "metadata_json": metadata}
    ).eq("id", log_id).execute()


async def execute(
    session_id: str,
    tool_name: str,
    params: Dict[str, Any],
    gateway_url: Optional[str] = None,
) -> dict:
    """
    Dispatch a tool call to OpenClaw and return {run_id, log_id}.
    Non-blocking – caller polls get_run() for completion.
    """
    log = _log_action(session_id, tool_name, "pending")
    log_id = log["id"]

    await status_event_service.publish(
        session_id, "tool.started", {"tool": tool_name, "log_id": log_id}
    )

    try:
        result = await openclaw_gateway_client.execute_task(tool_name, params, gateway_url)
        run_id = result.get("run_id", log_id)
        _update_log(log_id, "running", metadata={"run_id": run_id})
        logger.info("OpenClaw task dispatched: tool=%s run_id=%s", tool_name, run_id)
        return {"run_id": run_id, "log_id": log_id, "status": "running"}
    except Exception as exc:
        _update_log(log_id, "failed", message=str(exc))
        await status_event_service.publish(
            session_id, "tool.failed", {"tool": tool_name, "error": str(exc)}
        )
        logger.error("OpenClaw dispatch failed: %s", exc)
        raise


async def get_run(run_id: str, gateway_url: Optional[str] = None) -> dict:
    return await openclaw_gateway_client.get_run(run_id, gateway_url)


async def cancel(run_id: str, session_id: str, gateway_url: Optional[str] = None) -> dict:
    result = await openclaw_gateway_client.cancel_run(run_id, gateway_url)
    await status_event_service.publish(
        session_id, "tool.cancelled", {"run_id": run_id}
    )
    logger.info("OpenClaw run cancelled: %s", run_id)
    return result


async def complete_run(session_id: str, tool_name: str, run_id: str) -> None:
    """Call this when polling detects a completed run."""
    await status_event_service.publish(
        session_id, "tool.completed", {"tool": tool_name, "run_id": run_id}
    )
