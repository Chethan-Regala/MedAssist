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

