from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict

from app.utils import configure_logging


class MetricsCollector:
    """Simple metrics collection for agent performance."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.logger = configure_logging()
    
    def record_agent_execution(self, agent_name: str, duration: float, success: bool):
        """Record agent execution metrics."""
        self.metrics[f"{agent_name}_duration"].append(duration)
        self.counters[f"{agent_name}_total"] += 1
        if success:
            self.counters[f"{agent_name}_success"] += 1
        else:
            self.counters[f"{agent_name}_failure"] += 1
    
    def record_tool_usage(self, tool_name: str, success: bool):
        """Record tool usage metrics."""
        self.counters[f"tool_{tool_name}_total"] += 1
        if success:
            self.counters[f"tool_{tool_name}_success"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        summary = {"counters": dict(self.counters)}
        
        # Calculate averages for durations
        for key, values in self.metrics.items():
            if values and key.endswith("_duration"):
                summary[f"{key}_avg"] = sum(values) / len(values)
                summary[f"{key}_count"] = len(values)
        
        return summary


# Global metrics instance
metrics = MetricsCollector()


def track_execution(agent_name: str):
    """Decorator to track agent execution time and success."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                metrics.logger.error(f"{agent_name} execution failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_agent_execution(agent_name, duration, success)
        return wrapper
    return decorator