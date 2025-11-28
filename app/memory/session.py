from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils import configure_logging


class InMemorySessionService:
    """In-memory session management for agent conversations."""
    
    def __init__(self, max_sessions: int = 1000, session_ttl_hours: int = 24):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.max_sessions = max_sessions
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self.logger = configure_logging()
    
    def create_session(self, user_id: str) -> str:
        """Create new session for user."""
        session_id = str(uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "messages": [],
            "context": {},
            "health_summary": {}
        }
        self._cleanup_old_sessions()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if session:
            session["last_accessed"] = datetime.utcnow()
        return session
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to session."""
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            })
    
    def update_context(self, session_id: str, key: str, value: Any):
        """Update session context."""
        session = self.get_session(session_id)
        if session:
            session["context"][key] = value
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from session."""
        session = self.get_session(session_id)
        if session:
            return session["messages"][-limit:]
        return []
    
    def _cleanup_old_sessions(self):
        """Remove expired sessions."""
        cutoff = datetime.utcnow() - self.session_ttl
        expired = [
            sid for sid, session in self.sessions.items()
            if session["last_accessed"] < cutoff
        ]
        for sid in expired:
            del self.sessions[sid]
        
        # Limit total sessions
        if len(self.sessions) > self.max_sessions:
            oldest = sorted(
                self.sessions.items(),
                key=lambda x: x[1]["last_accessed"]
            )[:len(self.sessions) - self.max_sessions]
            for sid, _ in oldest:
                del self.sessions[sid]