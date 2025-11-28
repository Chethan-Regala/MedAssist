from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.agents.triage import TriageAgent
from app.tools.medical_tools import ToolRegistry
from app.schemas import TriageRequest, TriageResponse
from app.utils import configure_logging


class EnhancedTriageAgent(TriageAgent):
    """Enhanced triage agent with custom tool integration."""
    
    def __init__(self):
        super().__init__()
        self.tool_registry = ToolRegistry()
        self.logger = configure_logging()
    
    async def run_with_tools(
        self, 
        request: TriageRequest, 
        medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run triage with tool-enhanced analysis."""
        
        # Step 1: Basic triage
        triage_result = await self.run(request)
        
        # Step 2: Enhanced symptom analysis
        symptom_analysis = await self.tool_registry.execute_tool(
            "symptom_checker", 
            symptoms=request.symptoms
        )
        
        # Step 3: Drug interaction check if medications provided
        drug_analysis = None
        if medications:
            drug_analysis = await self.tool_registry.execute_tool(
                "drug_interaction",
                medications=medications
            )
        
        # Step 4: Combine results
        enhanced_result = {
            "basic_triage": triage_result.model_dump(),
            "symptom_analysis": symptom_analysis,
            "drug_analysis": drug_analysis,
            "tools_used": ["symptom_checker"] + (["drug_interaction"] if medications else []),
            "enhanced_recommendation": self._generate_enhanced_recommendation(
                triage_result, symptom_analysis, drug_analysis
            )
        }
        
        self.logger.info(f"Enhanced triage completed with {len(enhanced_result['tools_used'])} tools")
        return enhanced_result
    
    def _generate_enhanced_recommendation(
        self, 
        triage: TriageResponse, 
        symptom_analysis: Dict[str, Any],
        drug_analysis: Optional[Dict[str, Any]]
    ) -> str:
        """Generate enhanced recommendation based on tool outputs."""
        
        base_recommendation = triage.recommended_action
        
        # Enhance based on symptom analysis
        if symptom_analysis.get("primary_category") in ["cardiac", "neurological"]:
            if base_recommendation != "go_to_er":
                base_recommendation = "primary_care"
        
        # Enhance based on drug interactions
        if drug_analysis and drug_analysis.get("interactions_found", 0) > 0:
            return f"{base_recommendation} + consult pharmacist about drug interactions"
        
        return base_recommendation