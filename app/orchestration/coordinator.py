from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from app.agents.medication import MedicationSafetyAgent
from app.agents.triage import TriageAgent
from app.memory.memory_bank import MemoryBank
from app.memory.session import InMemorySessionService
from app.schemas import MedicationCheckRequest, TriageRequest
from app.utils import configure_logging


class AgentCoordinator:
    """Coordinates parallel and sequential agent execution."""
    
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.medication_agent = MedicationSafetyAgent()
        self.memory_bank = MemoryBank()
        self.session_service = InMemorySessionService()
        self.logger = configure_logging()
    
    async def parallel_health_assessment(
        self, 
        user_id: str, 
        symptoms: str, 
        medications: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run triage and medication check in parallel."""
        
        # Create session for this assessment
        session_id = self.session_service.create_session(user_id)
        
        # Prepare requests
        triage_request = TriageRequest(
            user_id=user_id,
            symptoms=symptoms,
            context=context
        )
        
        tasks = [
            self._run_triage_with_memory(triage_request, session_id)
        ]
        
        # Add medication check if medications provided
        if medications:
            med_request = MedicationCheckRequest(
                user_id=user_id,
                medications=medications
            )
            tasks.append(self._run_medication_check(med_request, session_id))
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        response = {"session_id": session_id}
        
        if len(results) >= 1 and not isinstance(results[0], Exception):
            response["triage"] = results[0]
        
        if len(results) >= 2 and not isinstance(results[1], Exception):
            response["medication_safety"] = results[1]
        
        # Add coordination summary
        response["coordination"] = self._create_coordination_summary(response)
        
        return response
    
    async def _run_triage_with_memory(self, request: TriageRequest, session_id: str) -> Dict[str, Any]:
        """Run triage with memory context."""
        # Get historical context
        health_summary = self.memory_bank.get_user_health_summary(request.user_id)
        contextual_history = self.memory_bank.get_contextual_history(
            request.user_id, 
            request.symptoms
        )
        
        # Update session context
        self.session_service.update_context(session_id, "health_summary", health_summary)
        self.session_service.add_message(
            session_id, 
            "user", 
            request.symptoms,
            {"type": "symptom_report"}
        )
        
        # Enhanced request with memory
        enhanced_context = f"{request.context or ''}\nHistory: {contextual_history}"
        enhanced_request = TriageRequest(
            user_id=request.user_id,
            symptoms=request.symptoms,
            context=enhanced_context
        )
        
        result = await self.triage_agent.run(enhanced_request)
        
        # Store result in session
        self.session_service.add_message(
            session_id,
            "assistant",
            f"Triage: {result.category} ({result.urgency})",
            {"type": "triage_result", "result": result.model_dump()}
        )
        
        return result.model_dump()
    
    async def _run_medication_check(self, request: MedicationCheckRequest, session_id: str) -> Dict[str, Any]:
        """Run medication safety check."""
        result = await self.medication_agent.run(request)
        
        # Store in session
        self.session_service.add_message(
            session_id,
            "assistant", 
            f"Medication check: {result.risk_level} risk",
            {"type": "medication_result", "result": result.model_dump()}
        )
        
        return result.model_dump()
    
    def _create_coordination_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of coordinated agent results."""
        summary = {"agents_executed": []}
        
        if "triage" in results:
            summary["agents_executed"].append("triage")
            triage = results["triage"]
            summary["primary_concern"] = f"{triage.get('category')} ({triage.get('urgency')} urgency)"
        
        if "medication_safety" in results:
            summary["agents_executed"].append("medication_safety")
            med = results["medication_safety"]
            summary["medication_risk"] = med.get("risk_level")
        
        # Cross-agent insights
        if "triage" in results and "medication_safety" in results:
            triage_urgency = results["triage"].get("urgency")
            med_risk = results["medication_safety"].get("risk_level")
            
            if triage_urgency == "high" and med_risk == "high":
                summary["coordination_alert"] = "Both symptom urgency and medication risk are high - immediate medical attention recommended"
            elif triage_urgency == "high" or med_risk == "high":
                summary["coordination_alert"] = "Elevated concern detected - consider medical consultation"
        
        return summary