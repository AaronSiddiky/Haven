import logging
from typing import Any, Dict

from app.browser import get_page

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    selector = params.get("selector", "")
    text = params.get("text", "")
    if not selector or not text:
        return {"error": "selector and text are required"}

    page = get_page()
    await page.fill(selector, text, timeout=10_000)
    logger.info("[%s] Typed into '%s'", run_id, selector)
    return {"filled": selector, "text": text}
