from __future__ import annotations

from typing import Dict, List, Optional

from app.agents.llm_client import LLMClient
from app.prompts import TRIAGE_PROMPT_TEMPLATE
from app.schemas import TriageRequest, TriageResponse
from app.tools.manager import ToolManager
from app.utils import configure_logging, safe_json_loads
from app.observability.metrics import track_execution
from app.observability.tracing import trace_operation


class RedFlagEngine:
    """Deterministic keyword scanner for dangerous presentations with severity tiers.

    - critical: force immediate ER escalation (true red flags)
    - urgent: raise minimum triage severity but do not force ER alone
    """

    def __init__(self) -> None:
        # Critical red flags that should always escalate to ER
        self.critical_phrases: Dict[str, str] = {
            # Cardiac/respiratory
            "chest pain": "Possible cardiac emergency.",
            "heart pain": "Possible cardiac emergency.",
            "pressure in chest": "Possible cardiac emergency.",
            "tightness in chest": "Possible cardiac emergency.",
            "pain radiating to left arm": "Possible myocardial infarction.",
            "jaw pain": "Possible cardiac ischemia.",
            "trouble breathing": "Respiratory distress risk.",
            "shortness of breath at rest": "Respiratory distress risk.",
            "blue lips": "Hypoxia.",
            # Neurological emergency
            "worst headache of my life": "Possible subarachnoid hemorrhage.",
            "severe headache": "Neurological emergency risk.",
            "sudden vision loss": "Stroke or neurological emergency.",
            "weakness on one side": "Stroke risk.",
            "difficulty speaking": "Stroke risk.",
            "loss of consciousness": "Altered mental status.",
            "seizure": "New seizure or status epilepticus risk.",
            # Hemorrhage/sepsis/anaphylaxis/trauma
            "uncontrolled bleeding": "Hemorrhage risk.",
            "vomiting blood": "GI bleed risk.",
            "coughing up blood": "Hemoptysis.",
            "black tarry stools": "GI bleeding.",
            "stiff neck with fever": "Possible meningitis.",
            "swollen tongue": "Airway compromise.",
            "anaphylaxis": "Severe allergic reaction.",
            "severe burn": "Severe injury.",
            "major trauma": "Severe injury.",
            # Mental health crisis
            "suicidal": "Mental health crisis.",
            "not responsive": "Altered mental status.",
        }
        # Urgent (yellow flags) — warrant prompt care but not automatic ER
        self.urgent_phrases: Dict[str, str] = {
            "severe shortness of breath": "Respiratory distress risk.",
            "fainting": "Syncope — evaluate for serious causes.",
            "new confusion": "Acute cognitive change.",
            "severe abdominal pain": "Possible surgical abdomen.",
            "blood in urine": "Hematuria.",
            "persistent high fever": "Infection risk.",
            "dehydration": "Significant volume loss.",
            "severe back pain": "Possible serious etiology.",
        }

    def detect(self, text: str) -> Dict[str, List[str]]:
        lowered = text.lower()
        critical = [p for p in self.critical_phrases if p in lowered]
        urgent = [p for p in self.urgent_phrases if p in lowered]
        return {"critical": critical, "urgent": urgent}


class TriageAgent:
    """Coordinates rule-based safety checks with LLM reasoning."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        red_flag_engine: Optional[RedFlagEngine] = None,
        tool_manager: Optional[ToolManager] = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.red_flag_engine = red_flag_engine or RedFlagEngine()
        self.tool_manager = tool_manager or ToolManager()
        self.logger = configure_logging()

    @track_execution("triage_agent")
    async def run(self, request: TriageRequest) -> TriageResponse:
        with trace_operation(f"triage_analysis_{request.user_id}") as span:
            span.add_tag("user_id", request.user_id)
            span.add_tag("symptoms_length", len(request.symptoms))

            symptoms_blob = f"{request.symptoms} {request.context or ''}"
            flags = self.red_flag_engine.detect(symptoms_blob)
            span.add_tag("critical_flags_detected", len(flags["critical"]))
            span.add_tag("urgent_flags_detected", len(flags["urgent"]))
            # True red flags force ER escalation
            if flags["critical"]:
                span.add_tag("red_flag_override", True)
                span.log(f"Critical red flags detected: {flags['critical']}")
                self.logger.info("Critical red-flag override triggered: %s", flags["critical"])
                return TriageResponse(
                    category="emergency",
                    urgency="high",
                    recommended_action="go_to_er",
                    red_flags=flags["critical"],  # only critical items are red_flags
                    reasoning="Deterministic critical red-flag rule forced escalation.",
                )

            # Use tools to enhance context
            span.log("Gathering medical context")
            medical_info = await self._gather_medical_context(request.symptoms)
            span.add_tag("medical_context_available", bool(medical_info))

            prompt = TRIAGE_PROMPT_TEMPLATE.format(
                user_id=request.user_id,
                symptoms=request.symptoms,
                context=request.context or "None provided",
                medical_context=medical_info,
            )
            span.log("Calling LLM for triage analysis")
            raw_output = await self.llm_client.complete(prompt)
            parsed = safe_json_loads(raw_output)
            span.add_tag("llm_response_parsed", bool(parsed))

            if not parsed:
                span.log("LLM response parsing failed, using fallback", "warning")
                self.logger.warning("LLM response parsing failed; falling back to safe mode.")
                # Apply minimum severity if urgent flags were detected
                urgency = "moderate" if flags["urgent"] else "moderate"
                action = "primary_care"
                return TriageResponse(
                    category="general",
                    urgency=urgency,
                    recommended_action=action,
                    red_flags=[],
                    reasoning="Fallback response due to parsing failure.",
                )

            # Post-process LLM output with guardrails: do not over-flag, but enforce minimums
            category = parsed.get("category", "general")
            urgency = parsed.get("urgency", "moderate")
            action = parsed.get("recommended_action", "primary_care")
            reasoning = parsed.get("reasoning", "LLM reasoning unavailable.")
            llm_red_flags = parsed.get("red_flags", [])

            # Ensure red_flags only contain critical items from our deterministic set
            filtered_red_flags = [rf for rf in llm_red_flags if rf in self.red_flag_engine.critical_phrases]

            # If any urgent flags present, enforce a minimum urgency of moderate and at least primary care
            if flags["urgent"]:
                if urgency == "low":
                    urgency = "moderate"
                # Ensure action is at least primary care
                if action == "self_care":
                    action = "primary_care"

            span.add_tag("final_urgency", urgency)
            span.add_tag("final_action", action)
            span.log(f"Triage completed: {category} ({urgency})")
            
            return TriageResponse(
                category=category,
                urgency=urgency,
                recommended_action=action,
                red_flags=filtered_red_flags,  # keep red_flags to true critical items only
                reasoning=reasoning,
            )
    
    async def _gather_medical_context(self, symptoms: str) -> str:
        """Use tools to gather additional medical context."""
        try:
            # Use medical lookup tool
            lookup_result = await self.tool_manager.execute_tool(
                "medical_lookup", 
                query=symptoms[:50],  # Limit query length
                lookup_type="conditions"
            )
            
            if lookup_result.get("success"):
                conditions = lookup_result.get("results", [])
                # Ensure conditions are strings
                condition_strs = [str(c) for c in conditions[:3] if c]
                if condition_strs:
                    return f"Related conditions: {', '.join(condition_strs)}"
                else:
                    return "No related conditions found."
            else:
                return "No additional medical context available."
        except Exception as e:
            self.logger.warning(f"Failed to gather medical context: {e}")
            return "Medical context lookup unavailable."

