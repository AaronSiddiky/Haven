import base64
import logging
from typing import Any, Dict

from app.browser import screenshot

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    png_bytes = await screenshot()
    b64 = base64.b64encode(png_bytes).decode()
    logger.info("[%s] Screenshot taken (%d bytes)", run_id, len(png_bytes))
    return {"screenshot_base64": b64, "format": "png"}
