from fastapi import APIRouter, Header

from app.db.repositories import user_repository
from app.schemas.preferences import PreferencesUpdate

router = APIRouter()

_DEFAULTS = {
    "minimum_severity": "watch",
    "voice_interruptions": True,
    "sms_notifications": False,
    "hazard_types_filter": [],
}


@router.get("")
def get_preferences(x_user_id: str = Header(...)):
    prefs = user_repository.get_preferences(x_user_id)
    return prefs or {**_DEFAULTS, "user_id": x_user_id}


@router.post("")
def upsert_preferences(body: PreferencesUpdate, x_user_id: str = Header(...)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    return user_repository.upsert_preferences(x_user_id, updates)
