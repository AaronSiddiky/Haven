"""
General-purpose task execution.

Receives a natural language instruction and performs it using
Playwright.  For now this maps simple verbs to direct actions;
a future version can integrate OpenAI Vision for multi-step
browser automation.
"""
import logging
from typing import Any, Dict

from app.browser import get_page

logger = logging.getLogger(__name__)


async def handle(params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    instruction = params.get("instruction", "")
    if not instruction:
        return {"error": "instruction is required"}

    page = get_page()
    logger.info("[%s] Executing task: %s", run_id, instruction)

    lower = instruction.lower().strip()

    if lower.startswith("go to ") or lower.startswith("open ") or lower.startswith("navigate to "):
        url = instruction.split(maxsplit=2)[-1].strip()
        if not url.startswith("http"):
            url = f"https://{url}"
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        return {"action": "navigate", "url": page.url, "title": await page.title()}

    if lower.startswith("search for ") or lower.startswith("search ") or lower.startswith("google "):
        from urllib.parse import quote_plus
        query = instruction.split(maxsplit=2)[-1].strip()
        await page.goto(
            f"https://www.google.com/search?q={quote_plus(query)}",
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        return {"action": "search", "query": query, "url": page.url}

    if lower.startswith("click "):
        selector = instruction.split(maxsplit=1)[-1].strip()
        await page.click(selector, timeout=10_000)
        return {"action": "click", "selector": selector}

    if lower.startswith("type "):
        parts = instruction.split(" into ", 1)
        if len(parts) == 2:
            text = parts[0].replace("type ", "", 1).strip().strip('"').strip("'")
            selector = parts[1].strip()
            await page.fill(selector, text, timeout=10_000)
            return {"action": "type", "selector": selector, "text": text}

    return {
        "action": "unsupported",
        "message": f"Could not parse instruction: {instruction}",
        "url": page.url,
        "title": await page.title(),
    }
