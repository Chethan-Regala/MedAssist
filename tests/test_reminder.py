import asyncio
from datetime import datetime, timedelta

import pytest

from app.agents.reminder import ReminderLoopAgent
from app.db.db import session_scope
from app.db.models import MedicationCheck, ReminderEvent, User
from sqlmodel import select


@pytest.mark.asyncio
async def test_reminder_generated_for_stale_med_check():
    user_id = "reminder-user"
    with session_scope() as session:
        existing = session.exec(select(User).where(User.user_id == user_id)).first()
        if not existing:
            session.add(User(user_id=user_id))
            session.commit()
        stale_check = MedicationCheck(
            user_id=user_id,
            medications=["testpill"],
            risk_level="low",
            conflicts=[],
            guidance="",
            created_at=datetime.utcnow() - timedelta(days=8),
        )
        session.add(stale_check)
        session.commit()

    agent = ReminderLoopAgent(interval_seconds=1)
    await agent.run_once()

    with session_scope() as session:
        reminder = session.exec(
            select(ReminderEvent)
            .where(ReminderEvent.user_id == user_id)
            .where(ReminderEvent.reminder_type == "medication_followup")
            .order_by(ReminderEvent.created_at.desc())
        ).first()
        assert reminder is not None

