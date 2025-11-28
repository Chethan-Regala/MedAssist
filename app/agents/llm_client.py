from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, Optional

import google.generativeai as genai
from google.generativeai import types as genai_types
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
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self._model = genai.GenerativeModel(self.settings.gemini_model)
                self.logger.info(f"Initialized Gemini model: {self.settings.gemini_model}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self._model = None
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
        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai_types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ]
            )
            
            # Check if response was blocked
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason.name == 'SAFETY':
                    self.logger.warning("Response blocked by safety filters")
                    return json.dumps(self._fallback(prompt))
            
            # Try to get text content
            if hasattr(response, 'text') and response.text:
                return response.text
            elif response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    return candidate.content.parts[0].text
            
            self.logger.warning("No valid text content in response")
            return json.dumps(self._fallback(prompt))
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            raise

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

