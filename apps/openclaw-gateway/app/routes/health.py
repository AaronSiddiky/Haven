from fastapi import APIRouter

from app import browser

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "browser": "running" if browser.is_running() else "stopped",
    }
