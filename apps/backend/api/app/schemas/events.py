from typing import Any, Dict, Optional

from pydantic import BaseModel


class HavenEvent(BaseModel):
    type: str
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
