from __future__ import annotations

from typing import Dict, List, Optional

from app.agents.llm_client import LLMClient
from app.prompts import TRIAGE_PROMPT_TEMPLATE
from app.schemas import TriageRequest, TriageResponse
from app.utils import configure_logging, safe_json_loads


class RedFlagEngine:
    """Deterministic keyword scanner for dangerous presentations."""

    def __init__(self) -> None:
        self.rules: Dict[str, str] = {
            "chest pain": "Possible cardiac emergency.",
            "shortness of breath": "Respiratory distress risk.",
            "trouble breathing": "Respiratory distress risk.",
            "severe headache": "Neurological emergency risk.",
            "sudden vision loss": "Stroke or neurological emergency.",
            "weakness on one side": "Stroke risk.",
            "uncontrolled bleeding": "Hemorrhage risk.",
            "suicidal": "Mental health crisis.",
            "not responsive": "Altered mental status.",
        }

    def detect(self, text: str) -> List[str]:
        lowered = text.lower()
        return [phrase for phrase in self.rules if phrase in lowered]


class TriageAgent:
    """Coordinates rule-based safety checks with LLM reasoning."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        red_flag_engine: Optional[RedFlagEngine] = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.red_flag_engine = red_flag_engine or RedFlagEngine()
        self.logger = configure_logging()

    async def run(self, request: TriageRequest) -> TriageResponse:
        symptoms_blob = f"{request.symptoms} {request.context or ''}"
        red_flags = self.red_flag_engine.detect(symptoms_blob)
        if red_flags:
            self.logger.info("Red-flag override triggered: %s", red_flags)
            return TriageResponse(
                category="emergency",
                urgency="high",
                recommended_action="go_to_er",
                red_flags=red_flags,
                reasoning="Deterministic red-flag rule forced escalation.",
            )

        prompt = TRIAGE_PROMPT_TEMPLATE.format(
            user_id=request.user_id,
            symptoms=request.symptoms,
            context=request.context or "None provided",
        )
        raw_output = await self.llm_client.complete(prompt)
        parsed = safe_json_loads(raw_output)

        if not parsed:
            self.logger.warning("LLM response parsing failed; falling back to safe mode.")
            return TriageResponse(
                category="general",
                urgency="moderate",
                recommended_action="primary_care",
                red_flags=[],
                reasoning="Fallback response due to parsing failure.",
            )

        return TriageResponse(
            category=parsed.get("category", "general"),
            urgency=parsed.get("urgency", "moderate"),
            recommended_action=parsed.get("recommended_action", "primary_care"),
            red_flags=parsed.get("red_flags", []),
            reasoning=parsed.get("reasoning", "LLM reasoning unavailable."),
        )

