from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User profile storing a stable identifier for a MedAssist member."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    full_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class SymptomEvent(SQLModel, table=True):
    """Persistent record of a triage interaction."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", index=True)
    symptoms: str
    context: Optional[str] = Field(default=None)

    category: str
    urgency: str
    recommended_action: str
    reasoning: str
    red_flags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MedicationCheck(SQLModel, table=True):
    """Record of a medication safety assessment."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    medications: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    risk_level: str
    conflicts: list[dict[str, str]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    guidance: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReminderEvent(SQLModel, table=True):
    """Loop agent output capturing reminders that were generated."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    reminder_type: str = Field(default="medication_followup")
    status: str = Field(default="pending")
    message: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReminderTask(SQLModel, table=True):
    """Long-running reminder configuration per user."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    reminder_type: str = Field(default="medication_check")
    cadence_minutes: int = Field(default=10080)  # weekly by default
    next_run_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True)
    message_template: str = Field(
        default="Time to review your medications and symptom status."
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReminderDelivery(SQLModel, table=True):
    """Record of reminder executions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="remindertask.id")
    user_id: str = Field(index=True)
    message: str
    delivered_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

