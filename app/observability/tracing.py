from __future__ import annotations

import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.utils import configure_logging

# Context variable for trace ID
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


class TraceSpan:
    """Individual span in a distributed trace."""
    
    def __init__(self, name: str, trace_id: str, parent_id: Optional[str] = None):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.name = name
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.tags: Dict[str, Any] = {}
        self.logs: List[Dict[str, Any]] = []
    
    def add_tag(self, key: str, value: Any):
        """Add tag to span."""
        self.tags[key] = value
    
    def log(self, message: str, level: str = "info"):
        """Add log entry to span."""
        self.logs.append({
            "timestamp": datetime.utcnow(),
            "level": level,
            "message": message
        })
    
    def finish(self):
        """Mark span as completed."""
        self.end_time = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": (
                (self.end_time - self.start_time).total_seconds() * 1000
                if self.end_time else None
            ),
            "tags": self.tags,
            "logs": self.logs
        }


class SimpleTracer:
    """Simple distributed tracing implementation."""
    
    def __init__(self):
        self.spans: Dict[str, List[TraceSpan]] = {}
        self.logger = configure_logging()
    
    def start_trace(self, operation_name: str) -> str:
        """Start new trace."""
        trace_id = str(uuid.uuid4())[:16]
        trace_id_var.set(trace_id)
        
        root_span = TraceSpan(operation_name, trace_id)
        self.spans[trace_id] = [root_span]
        
        self.logger.info(f"Started trace {trace_id} for {operation_name}")
        return trace_id
    
    def start_span(self, name: str, parent_id: Optional[str] = None) -> TraceSpan:
        """Start new span in current trace."""
        trace_id = trace_id_var.get()
        if not trace_id:
            trace_id = self.start_trace(name)
        
        span = TraceSpan(name, trace_id, parent_id)
        if trace_id not in self.spans:
            self.spans[trace_id] = []
        self.spans[trace_id].append(span)
        
        return span
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get complete trace by ID."""
        spans = self.spans.get(trace_id, [])
        return [span.to_dict() for span in spans]
    
    def get_active_traces(self) -> Dict[str, int]:
        """Get summary of active traces."""
        return {
            trace_id: len(spans) 
            for trace_id, spans in self.spans.items()
        }


# Global tracer instance
tracer = SimpleTracer()


class trace_operation:
    """Context manager for tracing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.span: Optional[TraceSpan] = None
    
    def __enter__(self) -> TraceSpan:
        self.span = tracer.start_span(self.operation_name)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.add_tag("error", True)
                self.span.log(f"Error: {exc_val}", "error")
            self.span.finish()