from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
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


@router.get("/screen/publisher-token")
def publisher_token():
    """Mint a LiveKit publisher token locally — no need to reach the Haven API."""
    settings = get_settings()
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise HTTPException(status_code=500, detail="LiveKit not configured on gateway")

    from livekit.api import AccessToken, VideoGrants

    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity("haven-worker")
        .with_ttl(timedelta(hours=4))
        .with_grants(
            VideoGrants(
                room_join=True,
                room="haven-demo",
                can_publish=True,
                can_subscribe=False,
                can_publish_data=True,
            )
        )
    )
    return {
        "token": token.to_jwt(),
        "ws_url": settings.livekit_ws_url,
        "room_name": "haven-demo",
        "identity": "haven-worker",
    }
