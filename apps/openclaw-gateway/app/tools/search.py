import logging
from typing import Any, Dict
from urllib.parse import quote_plus

from app.browser import get_page

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    query = params.get("query", "")
    if not query:
        return {"error": "query is required"}

    page = get_page()
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    await page.goto(search_url, wait_until="domcontentloaded", timeout=30_000)
    title = await page.title()
    logger.info("[%s] Searched for '%s'", run_id, query)
    return {"title": title, "url": page.url, "query": query}
