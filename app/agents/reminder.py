from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select

from app.db.db import session_scope
from app.db.models import MedicationCheck, ReminderEvent, SymptomEvent, User
from app.utils import configure_logging


class ReminderLoopAgent:
    """Loop agent that periodically scans user data and emits reminders."""

    def __init__(self, interval_seconds: int = 3600) -> None:
        self.interval_seconds = interval_seconds
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.job_id = "medassist-reminder-loop"
        self.logger = configure_logging()
        self._is_running = False

    def start(self) -> None:
        if self._is_running:
            return
        self.scheduler.add_job(
            self._run_cycle,
            "interval",
            seconds=self.interval_seconds,
            id=self.job_id,
            max_instances=1,
        )
        self.scheduler.start()
        self._is_running = True
        self.logger.info("Reminder loop agent started (interval=%ss)", self.interval_seconds)

    def shutdown(self) -> None:
        if not self._is_running:
            return
        self.scheduler.shutdown(wait=False)
        self._is_running = False
        self.logger.info("Reminder loop agent stopped")

    def pause(self) -> None:
        if self.scheduler.get_job(self.job_id):
            self.scheduler.pause_job(self.job_id)
            self.logger.info("Reminder loop agent paused")

    def resume(self) -> None:
        if self.scheduler.get_job(self.job_id):
            self.scheduler.resume_job(self.job_id)
            self.logger.info("Reminder loop agent resumed")

    @property
    def status(self) -> dict[str, object]:
        job = self.scheduler.get_job(self.job_id)
        is_running = self._is_running and job is not None and job.next_run_time is not None
        return {
            "running": is_running,
            "next_run_time": job.next_run_time.isoformat() if job and job.next_run_time else None,
        }

    async def _run_cycle(self) -> None:
        """Scheduled job entry point."""

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._scan_and_emit)

    def _scan_and_emit(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        with session_scope() as session:
            users = session.exec(select(User)).all()
            for user in users:
                if self._needs_medication_followup(session, user.user_id, cutoff):
                    if self._recent_reminder_exists(session, user.user_id):
                        continue
                    message = (
                        f"User {user.user_id} has no medication safety check in the last 7 days."
                    )
                    reminder = ReminderEvent(
                        user_id=user.user_id,
                        reminder_type="medication_followup",
                        status="pending",
                        message=message,
                    )
                    session.add(reminder)
                    self.logger.info("Reminder generated: %s", message)

    def _needs_medication_followup(
        self, session: Session, user_id: str, cutoff: datetime
    ) -> bool:
        latest_check = session.exec(
            select(MedicationCheck)
            .where(MedicationCheck.user_id == user_id)
            .order_by(MedicationCheck.created_at.desc())
        ).first()
        if latest_check:
            return latest_check.created_at.replace(tzinfo=timezone.utc) < cutoff

        latest_event = session.exec(
            select(SymptomEvent)
            .where(SymptomEvent.user_id == user_id)
            .order_by(SymptomEvent.created_at.desc())
        ).first()
        if latest_event:
            return latest_event.created_at.replace(tzinfo=timezone.utc) < cutoff
        return False

    def _recent_reminder_exists(self, session: Session, user_id: str) -> bool:
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        existing = session.exec(
            select(ReminderEvent)
            .where(ReminderEvent.user_id == user_id)
            .where(ReminderEvent.reminder_type == "medication_followup")
            .where(ReminderEvent.created_at >= recent_cutoff)
        ).first()
        return existing is not None

    async def run_once(self) -> None:
        """Manual trigger for tests."""

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._scan_and_emit)
