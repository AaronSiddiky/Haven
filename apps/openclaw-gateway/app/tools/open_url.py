import logging
from typing import Any, Dict

from app.browser import get_page

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    url = params.get("url", "")
    if not url:
        return {"error": "url is required"}

    page = get_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    title = await page.title()
    logger.info("[%s] Navigated to %s (%s)", run_id, url, title)
    return {"title": title, "url": page.url}
