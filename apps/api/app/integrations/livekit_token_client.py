"""
Thin wrapper around livekit-api token generation.
Signs tokens locally — no network calls.
"""
import logging
from datetime import timedelta

from livekit.api import AccessToken, VideoGrants

from app.core.config import get_settings

logger = logging.getLogger(__name__)
TTL = timedelta(hours=4)


def _build_token(identity: str, room: str, can_publish: bool, can_subscribe: bool) -> str:
    settings = get_settings()
    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_ttl(TTL)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=can_publish,
                can_subscribe=can_subscribe,
                can_publish_data=can_publish,
            )
        )
    )
    return token.to_jwt()


def mint_operator_token(room: str, identity: str = "haven-operator") -> str:
    """Subscriber-only token for the Haven frontend."""
    return _build_token(identity, room, can_publish=False, can_subscribe=True)


def mint_worker_token(room: str, identity: str = "haven-worker") -> str:
    """Publisher token for the worker screen-share page."""
    return _build_token(identity, room, can_publish=True, can_subscribe=False)
