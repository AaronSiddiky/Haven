import logging
from typing import Any, Dict

from app.browser import get_page

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    selector = params.get("selector", "")
    if not selector:
        return {"error": "selector is required"}

    page = get_page()
    await page.click(selector, timeout=10_000)
    logger.info("[%s] Clicked '%s'", run_id, selector)
    return {"clicked": selector}
