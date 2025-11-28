from __future__ import annotations

from typing import Any, Dict, List

from app.utils import configure_logging


class ContextCompactor:
    """Context engineering for managing long conversation histories."""
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.logger = configure_logging()
    
    def compact_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compact message history to fit within token limits."""
        if not messages:
            return []
        
        # Estimate tokens (rough: 4 chars = 1 token)
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_tokens = total_chars // 4
        
        if estimated_tokens <= self.max_tokens:
            return messages
        
        # Keep first and last messages, summarize middle
        if len(messages) <= 3:
            return messages[-2:]  # Keep last 2
        
        first_msg = messages[0]
        last_msgs = messages[-3:]  # Keep last 3
        middle_msgs = messages[1:-3]
        
        # Create summary of middle messages
        summary = self._summarize_messages(middle_msgs)
        summary_msg = {
            "role": "system",
            "content": f"[Summary of {len(middle_msgs)} previous messages: {summary}]",
            "timestamp": middle_msgs[-1]["timestamp"] if middle_msgs else None,
            "metadata": {"type": "summary"}
        }
        
        return [first_msg, summary_msg] + last_msgs
    
    def compact_health_context(self, health_data: Dict[str, Any]) -> str:
        """Compact health history into concise context."""
        if not health_data:
            return "No health history available."
        
        summary_parts = []
        
        # Recent activity
        if health_data.get("symptom_events", 0) > 0:
            summary_parts.append(f"{health_data['symptom_events']} recent symptoms")
        
        # Categories
        if health_data.get("recent_categories"):
            categories = ", ".join(health_data["recent_categories"][:3])
            summary_parts.append(f"categories: {categories}")
        
        # Patterns
        patterns = health_data.get("patterns", {})
        if patterns.get("trend") == "concerning":
            summary_parts.append("concerning trend detected")
        
        return "; ".join(summary_parts) if summary_parts else "Stable health profile"
    
    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Create brief summary of message sequence."""
        if not messages:
            return "No messages"
        
        user_msgs = [m for m in messages if m.get("role") == "user"]
        system_msgs = [m for m in messages if m.get("role") == "assistant"]
        
        summary = f"{len(user_msgs)} user queries, {len(system_msgs)} responses"
        
        # Add key topics if available
        if user_msgs:
            last_user_msg = user_msgs[-1]["content"][:50]
            summary += f", last topic: {last_user_msg}..."
        
        return summary