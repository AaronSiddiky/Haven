from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ContactCreate(BaseModel):
    name: str
    phone: str
    relationship: Optional[str] = None
    notify_automatically: bool = False


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relationship: Optional[str] = None
    notify_automatically: Optional[bool] = None


class ContactResponse(BaseModel):
    id: UUID
    user_id: str
    name: str
    phone: str
    relationship: Optional[str] = None
    notify_automatically: bool
