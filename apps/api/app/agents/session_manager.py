"""
Manages in-memory conversation state per voice session.

Tracks: currently focused alert, turn history, user refinements.
State is ephemeral — reloaded from DB transcript on reconnect.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConversationState:
    session_id: str
    user_id: str
    focused_alert_id: Optional[str] = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    turns: List[Dict] = field(default_factory=list)
    pending_approval: Optional[Dict] = None

    def add_turn(self, speaker: str, text: str) -> None:
        self.turns.append({
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def set_focus(self, alert_id: str) -> None:
        self.focused_alert_id = alert_id
        logger.debug("Session %s focused on alert %s", self.session_id, alert_id)

    def request_approval(self, action_type: str, payload: Dict) -> None:
        self.pending_approval = {"action_type": action_type, "payload": payload}

    def clear_approval(self) -> Optional[Dict]:
        approval = self.pending_approval
        self.pending_approval = None
        return approval


class SessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationState] = {}

    def create(self, session_id: str, user_id: str) -> ConversationState:
        state = ConversationState(session_id=session_id, user_id=user_id)
        self._sessions[session_id] = state
        logger.info("Voice session created: %s  user=%s", session_id, user_id)
        return state

    def get(self, session_id: str) -> Optional[ConversationState]:
        return self._sessions.get(session_id)

    def end(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        logger.info("Voice session ended: %s", session_id)

    def all_sessions(self) -> List[str]:
        return list(self._sessions.keys())


session_manager = SessionManager()
