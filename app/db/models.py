from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User profile storing a stable identifier for a MedAssist member."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    full_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    events: List["SymptomEvent"] = Relationship(back_populates="user")


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

    user: Optional[User] = Relationship(back_populates="events")

