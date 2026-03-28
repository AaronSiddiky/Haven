"""
Playwright browser manager.

Launches a headed Chromium instance and exposes the active page
for tool handlers to drive.
"""
import logging
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)

_pw = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None
_page: Optional[Page] = None


async def launch(headless: bool = False) -> Page:
    global _pw, _browser, _context, _page
    _pw = await async_playwright().start()
    _browser = await _pw.chromium.launch(headless=headless)
    _context = await _browser.new_context(viewport={"width": 1280, "height": 800})
    _page = await _context.new_page()
    logger.info("Playwright browser launched (headless=%s)", headless)
    return _page


def get_page() -> Page:
    if _page is None:
        raise RuntimeError("Browser not launched — call launch() first")
    return _page


def is_running() -> bool:
    return _browser is not None and _browser.is_connected()


async def screenshot() -> bytes:
    return await get_page().screenshot(type="png")


async def close() -> None:
    global _pw, _browser, _context, _page
    if _context:
        await _context.close()
    if _browser:
        await _browser.close()
    if _pw:
        await _pw.stop()
    _pw = _browser = _context = _page = None
    logger.info("Playwright browser closed")
