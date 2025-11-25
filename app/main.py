from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app.agents.triage import TriageAgent
from app.config import get_settings
from app.db.db import get_session, init_db
from app.db.models import SymptomEvent, User
from app.schemas import SymptomEventRead, TriageRequest, TriageResponse
from app.utils import configure_logging


settings = get_settings()
logger = configure_logging(settings.log_level)
agent = TriageAgent()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MedAssist triage backend MVP.",
)


@app.on_event("startup")
def startup() -> None:
    logger.info("Starting MedAssist API")
    init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
async def triage(
    payload: TriageRequest, session: Session = Depends(get_session)
) -> TriageResponse:
    result = await agent.run(payload)
    user = session.exec(select(User).where(User.user_id == payload.user_id)).first()
    if not user:
        user = User(user_id=payload.user_id)
        session.add(user)
        session.commit()
        session.refresh(user)

    event = SymptomEvent(
        user_id=payload.user_id,
        symptoms=payload.symptoms,
        context=payload.context,
        category=result.category,
        urgency=result.urgency,
        recommended_action=result.recommended_action,
        reasoning=result.reasoning,
        red_flags=result.red_flags,
    )
    session.add(event)
    session.commit()
    return result


@app.get("/users/{user_id}/events", response_model=List[SymptomEventRead])
def list_events(user_id: str, session: Session = Depends(get_session)) -> List[SymptomEventRead]:
    events = session.exec(
        select(SymptomEvent).where(SymptomEvent.user_id == user_id).order_by(
            SymptomEvent.created_at.desc()
        )
    ).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found for user.")
    return [SymptomEventRead.model_validate(event) for event in events]

