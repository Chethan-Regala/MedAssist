from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.agents.triage import TriageAgent
from app.agents.medication import MedicationSafetyAgent
from app.schemas import TriageRequest, TriageResponse, MedicationCheckRequest
from app.utils import configure_logging


class SequentialPipeline:
    """Sequential multi-agent pipeline for comprehensive health assessment."""

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.medication_agent = MedicationSafetyAgent()
        self.logger = configure_logging()

    async def run_health_assessment(
        self, 
        user_id: str, 
        symptoms: str, 
        context: Optional[str] = None,
        medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run sequential pipeline: triage -> medication check -> combined assessment."""
        
        results = {"user_id": user_id, "pipeline_steps": []}
        
        # Step 1: Triage Assessment
        triage_request = TriageRequest(
            user_id=user_id,
            symptoms=symptoms,
            context=context
        )
        triage_result = await self.triage_agent.run(triage_request)
        results["triage"] = triage_result.model_dump()
        results["pipeline_steps"].append("triage_completed")
        
        # Step 2: Medication Safety Check (if medications provided)
        if medications:
            med_request = MedicationCheckRequest(
                user_id=user_id,
                medications=medications
            )
            med_result = await self.medication_agent.run(med_request)
            results["medication_safety"] = med_result.model_dump()
            results["pipeline_steps"].append("medication_check_completed")
        
        # Step 3: Combined Risk Assessment
        combined_risk = self._assess_combined_risk(
            triage_result, 
            med_result if medications else None
        )
        results["combined_assessment"] = combined_risk
        results["pipeline_steps"].append("combined_assessment_completed")
        
        self.logger.info(f"Sequential pipeline completed for user {user_id}")
        return results

    def _assess_combined_risk(
        self, 
        triage: TriageResponse, 
        medication: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Combine triage and medication risks for final assessment."""
        
        risk_factors = []
        final_urgency = triage.urgency
        
        if triage.urgency == "high" or triage.recommended_action == "go_to_er":
            risk_factors.append("high_symptom_urgency")
            final_urgency = "high"
        
        if medication and medication.risk_level == "high":
            risk_factors.append("high_medication_risk")
            if final_urgency != "high":
                final_urgency = "moderate"
        
        return {
            "final_urgency": final_urgency,
            "risk_factors": risk_factors,
            "recommendation": self._get_final_recommendation(final_urgency, risk_factors)
        }
    
    def _get_final_recommendation(self, urgency: str, risk_factors: List[str]) -> str:
        """Generate final recommendation based on combined assessment."""
        
        if urgency == "high" or "high_symptom_urgency" in risk_factors:
            return "Seek immediate emergency care"
        elif "high_medication_risk" in risk_factors:
            return "Consult healthcare provider about medication interactions"
        else:
            return "Monitor symptoms and follow standard care recommendations"