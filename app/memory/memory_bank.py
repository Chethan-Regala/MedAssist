from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from app.db.db import session_scope
from app.db.models import MedicationCheck, SymptomEvent, User
from app.utils import configure_logging


class MemoryBank:
    """Long-term memory system for user health history and patterns."""
    
    def __init__(self):
        self.logger = configure_logging()
    
    def get_user_health_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive health summary for user."""
        with session_scope() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Get recent symptoms
            symptoms = session.exec(
                select(SymptomEvent)
                .where(SymptomEvent.user_id == user_id)
                .where(SymptomEvent.created_at >= cutoff)
                .order_by(SymptomEvent.created_at.desc())
            ).all()
            
            # Get medication checks
            med_checks = session.exec(
                select(MedicationCheck)
                .where(MedicationCheck.user_id == user_id)
                .where(MedicationCheck.created_at >= cutoff)
                .order_by(MedicationCheck.created_at.desc())
            ).all()
            
            return {
                "user_id": user_id,
                "period_days": days,
                "symptom_events": len(symptoms),
                "medication_checks": len(med_checks),
                "recent_categories": list(set(s.category for s in symptoms[:5])),
                "risk_levels": [m.risk_level for m in med_checks[:3]],
                "last_activity": symptoms[0].created_at if symptoms else None,
                "patterns": self._analyze_patterns(symptoms, med_checks)
            }
    
    def get_contextual_history(self, user_id: str, current_symptoms: str) -> str:
        """Get relevant historical context for current symptoms."""
        with session_scope() as session:
            # Get similar past events
            past_events = session.exec(
                select(SymptomEvent)
                .where(SymptomEvent.user_id == user_id)
                .order_by(SymptomEvent.created_at.desc())
                .limit(10)
            ).all()
            
            if not past_events:
                return "No previous health history available."
            
            # Simple keyword matching for relevance
            keywords = current_symptoms.lower().split()
            relevant_events = []
            
            for event in past_events:
                event_text = f"{event.symptoms} {event.context or ''}".lower()
                if any(keyword in event_text for keyword in keywords):
                    relevant_events.append(event)
            
            if relevant_events:
                latest = relevant_events[0]
                return f"Similar symptoms on {latest.created_at.date()}: {latest.category} ({latest.urgency} urgency)"
            else:
                return f"Last health check: {past_events[0].created_at.date()} - {past_events[0].category}"
    
    def _analyze_patterns(self, symptoms: List[SymptomEvent], med_checks: List[MedicationCheck]) -> Dict[str, Any]:
        """Analyze health patterns from historical data."""
        if not symptoms:
            return {"trend": "insufficient_data"}
        
        # Analyze urgency trends
        urgencies = [s.urgency for s in symptoms[:5]]
        high_urgency_count = urgencies.count("high")
        
        # Analyze category patterns
        categories = [s.category for s in symptoms]
        most_common = max(set(categories), key=categories.count) if categories else "none"
        
        return {
            "trend": "concerning" if high_urgency_count >= 2 else "stable",
            "most_common_category": most_common,
            "high_urgency_events": high_urgency_count,
            "total_events": len(symptoms)
        }