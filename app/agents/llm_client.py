from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import Settings, get_settings
from app.utils import configure_logging


class LLMClient:
    """Wrapper around Gemini with a deterministic offline fallback."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.logger = configure_logging(self.settings.log_level)
        self._model = None
        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self._model = genai.GenerativeModel(self.settings.gemini_model)
        else:
            self.logger.warning(
                "GEMINI_API_KEY not set; using heuristic fallback for triage responses."
            )

    async def complete(self, prompt: str) -> str:
        """Generate structured output for the given prompt."""

        if not self._model:
            return json.dumps(self._fallback(prompt))

        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, self._sync_completion, prompt)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("LLM call failed, using fallback: %s", exc)
            return json.dumps(self._fallback(prompt))

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def _sync_completion(self, prompt: str) -> str:
        response = self._model.generate_content(prompt)
        return response.text or ""

    def _fallback(self, prompt: str) -> Dict[str, Any]:
        """Simple safety-first heuristic used when an API key is missing."""

        lower_prompt = prompt.lower()
        critical_terms = [
            "chest pain",
            "trouble breathing",
            "suicidal",
            "stroke",
            "bleeding",
            "severe headache",
        ]
        category = "general"
        urgency = "moderate"
        action = "primary_care"

        for term in critical_terms:
            if term in lower_prompt:
                category = "emergency"
                urgency = "high"
                action = "go_to_er"
                break

        if "rash" in lower_prompt:
            category = "dermatological"
        elif re.search(r"headache|vision|dizzy", lower_prompt):
            category = "neurological"
        elif re.search(r"breath|cough|lung", lower_prompt):
            category = "respiratory"

        return {
            "category": category,
            "urgency": urgency,
            "recommended_action": action,
            "red_flags": [],
            "reasoning": "Fallback heuristic response when LLM is unavailable.",
        }

