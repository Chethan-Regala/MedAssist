from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.agents.medication import MedicationSafetyAgent
from app.agents.reminder import ReminderLoopAgent
from app.agents.triage import TriageAgent
from app.orchestration.coordinator import AgentCoordinator
from app.observability.metrics import metrics
from app.observability.tracing import tracer
from app.evaluation.evaluator import AgentEvaluator
from app.protocols.a2a import a2a_protocol, AgentMessage

from app.config import get_settings
from app.db.db import get_session, init_db
from app.db.models import MedicationCheck, ReminderEvent, SymptomEvent, User
from app.schemas import (
    MedicationCheckRead,
    MedicationCheckRequest,
    MedicationCheckResponse,
    ReminderEventRead,
    SymptomEventRead,
    TriageRequest,
    TriageResponse,
)
from app.utils import configure_logging


settings = get_settings()
logger = configure_logging(settings.log_level)
triage_agent = TriageAgent()
med_agent = MedicationSafetyAgent()
reminder_agent = ReminderLoopAgent(interval_seconds=1800)
coordinator = AgentCoordinator()
evaluator = AgentEvaluator()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MedAssist triage backend MVP.",
)

# Enable CORS for local development and the static UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    logger.info("Starting MedAssist API")
    init_db()
    reminder_agent.start()
    
    # Register agents for A2A communication
    a2a_protocol.register_agent("triage", triage_agent)
    a2a_protocol.register_agent("medication", med_agent)
    a2a_protocol.register_agent("reminder", reminder_agent)


@app.on_event("shutdown")
def shutdown() -> None:
    reminder_agent.shutdown()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
async def triage(
    payload: TriageRequest, session: Session = Depends(get_session)
) -> TriageResponse:
    result = await triage_agent.run(payload)
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


@app.post("/medications/check", response_model=MedicationCheckResponse)
async def medication_check(
    payload: MedicationCheckRequest, session: Session = Depends(get_session)
) -> MedicationCheckResponse:
    response = await med_agent.run(payload)

    record = MedicationCheck(
        user_id=payload.user_id,
        medications=payload.medications,
        risk_level=response.risk_level,
        conflicts=[conflict.model_dump() for conflict in response.conflicts],
        guidance=response.guidance,
    )
    session.add(record)
    session.commit()

    return response


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


@app.get(
    "/users/{user_id}/medication-checks",
    response_model=List[MedicationCheckRead],
)
def list_medication_checks(
    user_id: str, session: Session = Depends(get_session)
) -> List[MedicationCheckRead]:
    results = session.exec(
        select(MedicationCheck)
        .where(MedicationCheck.user_id == user_id)
        .order_by(MedicationCheck.created_at.desc())
    ).all()
    if not results:
        raise HTTPException(status_code=404, detail="No medication checks found for user.")
    return [MedicationCheckRead.model_validate(item) for item in results]


@app.get(
    "/users/{user_id}/reminders",
    response_model=List[ReminderEventRead],
)
def list_reminders(
    user_id: str, session: Session = Depends(get_session)
) -> List[ReminderEventRead]:
    reminders = session.exec(
        select(ReminderEvent)
        .where(ReminderEvent.user_id == user_id)
        .order_by(ReminderEvent.created_at.desc())
    ).all()
    if not reminders:
        raise HTTPException(status_code=404, detail="No reminders found for user.")
    return [ReminderEventRead.model_validate(item) for item in reminders]


@app.post("/reminders/pause")
def pause_reminders() -> dict[str, str]:
    reminder_agent.pause()
    return {"status": "paused"}


@app.post("/reminders/resume")
def resume_reminders() -> dict[str, str]:
    reminder_agent.resume()
    return {"status": "running"}


@app.get("/reminders/status")
def reminder_status() -> dict[str, object]:
    return reminder_agent.status


@app.post("/health-assessment")
async def parallel_health_assessment(
    payload: dict, session: Session = Depends(get_session)
) -> dict:
    """Coordinated parallel health assessment."""
    result = await coordinator.parallel_health_assessment(
        user_id=payload["user_id"],
        symptoms=payload["symptoms"],
        medications=payload.get("medications"),
        context=payload.get("context")
    )
    return result


@app.get("/tools")
def list_tools() -> dict:
    """List available agent tools."""
    return {"tools": coordinator.triage_agent.tool_manager.list_tools()}


@app.get("/metrics")
def get_metrics() -> dict:
    """Get system metrics."""
    return metrics.get_summary()





@app.get("/traces")
def get_traces() -> dict:
    """Get active traces."""
    return {"active_traces": tracer.get_active_traces()}


@app.get("/traces/{trace_id}")
def get_trace(trace_id: str) -> dict:
    """Get specific trace details."""
    return {"trace": tracer.get_trace(trace_id)}


@app.post("/evaluate")
async def evaluate_agents() -> dict:
    """Run agent evaluation suite."""
    triage_eval = await evaluator.evaluate_triage_agent(triage_agent)
    return {"triage_evaluation": triage_eval}


@app.post("/test")
async def test_system() -> dict:
    """Test system functionality."""
    try:
        # Test triage agent
        test_request = TriageRequest(
            user_id="test-user",
            symptoms="mild headache",
            context="after working late"
        )
        triage_result = await triage_agent.run(test_request)
        
        return {
            "status": "success",
            "triage_test": {
                "category": triage_result.category,
                "urgency": triage_result.urgency,
                "action": triage_result.recommended_action
            },
            "tools_available": len(coordinator.triage_agent.tool_manager.list_tools()),
            "a2a_agents": len(a2a_protocol.agents),
            "system_healthy": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "system_healthy": False
        }


@app.post("/a2a/send")
async def send_a2a_message(payload: dict) -> dict:
    """Send agent-to-agent message."""
    message = AgentMessage(
        sender=payload["sender"],
        receiver=payload["receiver"],
        message_type=payload["type"],
        payload=payload["payload"]
    )
    
    success = await a2a_protocol.send_message(message)
    return {"success": success, "message_id": message.id}


@app.get("/a2a/history")
def get_a2a_history() -> dict:
    """Get A2A message history."""
    return {"messages": a2a_protocol.get_message_history()}




