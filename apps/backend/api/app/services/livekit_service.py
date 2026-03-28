"""
LiveKit token minting and room metadata.

Does NOT relay media – only creates tokens for the browser clients.
"""
import logging

from app.core.config import get_settings
from app.integrations.livekit_token_client import mint_operator_token, mint_worker_token

logger = logging.getLogger(__name__)


def get_operator_token(room_name: str, identity: str = "haven-operator") -> dict:
    """Return a subscriber token for the Haven frontend."""
    token = mint_operator_token(room_name, identity)
    settings = get_settings()
    logger.info("Operator token minted for room %s identity %s", room_name, identity)
    return {
        "token": token,
        "room_name": room_name,
        "ws_url": settings.livekit_ws_url,
        "identity": identity,
    }


def get_worker_token(room_name: str, identity: str = "haven-worker") -> dict:
    """Return a publisher token for the worker screen-share page."""
    token = mint_worker_token(room_name, identity)
    settings = get_settings()
    logger.info("Worker token minted for room %s identity %s", room_name, identity)
    return {
        "token": token,
        "room_name": room_name,
        "ws_url": settings.livekit_ws_url,
        "identity": identity,
    }
