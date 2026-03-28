from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import get_settings
from app.registration import get_session_id, get_worker_id

router = APIRouter()
STATIC_DIR = Path(__file__).parent.parent.parent / "static"


@router.get("/screen")
def screen_page():
    return FileResponse(STATIC_DIR / "screen.html", media_type="text/html")


@router.get("/screen/config")
def screen_config():
    settings = get_settings()
    return {
        "haven_api_url": settings.haven_api_url,
        "worker_id": get_worker_id(),
        "session_id": get_session_id(),
    }
