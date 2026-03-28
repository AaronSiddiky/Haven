"""
Tool: execute_computer_task

Sends a natural-language instruction to the OpenClaw gateway for
general-purpose browser automation.
"""
import logging
from typing import Any, Dict

from app.integrations import openclaw_client

logger = logging.getLogger(__name__)


async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    instruction: str = args.get("instruction", "")
    session_id: str = args.get("session_id", "")

    if not instruction:
        return {"error": "instruction is required"}

    try:
        result = await openclaw_client._execute(
            "execute_task",
            {"instruction": instruction, "session_id": session_id},
        )
        logger.info("Computer task dispatched: %s", instruction[:80])
        return {
            "status": "executed",
            "instruction": instruction,
            **result,
        }
    except Exception as exc:
        logger.error("execute_computer_task failed: %s", exc)
        return {
            "status": "error",
            "instruction": instruction,
            "message": str(exc),
        }
