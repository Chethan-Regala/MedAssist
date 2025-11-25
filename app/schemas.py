from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TriageRequest(BaseModel):
    user_id: str = Field(description="Stable identifier for the user.")
    symptoms: str = Field(description="Free-form user description of symptoms.")
    context: Optional[str] = Field(
        default=None, description="Optional medical history or recent events."
    )


class TriageResponse(BaseModel):
    category: str
    urgency: str
    recommended_action: str
    red_flags: List[str]
    reasoning: str


class SymptomEventRead(TriageResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    symptoms: str
    context: Optional[str]
    created_at: datetime


class MedicationConflict(BaseModel):
    medications: list[str]
    severity: str
    reason: str


class MedicationCheckRequest(BaseModel):
    user_id: str
    medications: list[str] = Field(
        description="List of medication names (brand or generic).", min_length=1
    )


class MedicationCheckResponse(BaseModel):
    risk_level: str
    conflicts: list[MedicationConflict]
    guidance: str


class MedicationCheckRead(MedicationCheckResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    medications: list[str]
    created_at: datetime


class ReminderEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    reminder_type: str
    status: str
    message: str
    created_at: datetime


class ReminderTaskCreate(BaseModel):
    user_id: str
    reminder_type: str = Field(default="medication_check")
    cadence_minutes: int = Field(default=10080, ge=15)
    message_template: str = Field(
        default="Time to review your medications and symptom status."
    )


class ReminderTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    reminder_type: str
    cadence_minutes: int
    next_run_at: datetime
    is_active: bool
    message_template: str
    created_at: datetime


class ReminderDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: str
    message: str
    delivered_at: datetime

