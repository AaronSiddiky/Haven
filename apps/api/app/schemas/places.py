from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlaceCreate(BaseModel):
    label: str
    address: Optional[str] = None
    lat: float
    lon: float
    radius_km: float = 25.0
    notify_on_watch: bool = True
    notify_on_warning: bool = True


class PlaceUpdate(BaseModel):
    label: Optional[str] = None
    radius_km: Optional[float] = None
    notify_on_watch: Optional[bool] = None
    notify_on_warning: Optional[bool] = None


class PlaceResponse(BaseModel):
    id: UUID
    user_id: str
    label: str
    address: Optional[str] = None
    lat: float
    lon: float
    radius_km: float
    notify_on_watch: bool
    notify_on_warning: bool
