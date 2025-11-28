from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
from app.utils import configure_logging


class DrugInteractionTool:
    """Custom tool for external drug interaction API."""
    
    def __init__(self):
        self.logger = configure_logging()
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
    
    async def check_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """Check drug interactions using RxNorm API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                interactions = []
                for med in medications:
                    # Get RxCUI for medication
                    rxcui = await self._get_rxcui(client, med)
                    if rxcui:
                        # Get interactions
                        med_interactions = await self._get_interactions(client, rxcui)
                        interactions.extend(med_interactions)
                
                return {
                    "tool": "drug_interaction_api",
                    "medications_checked": medications,
                    "interactions_found": len(interactions),
                    "interactions": interactions[:5]  # Limit results
                }
        except Exception as e:
            self.logger.error(f"Drug interaction API error: {e}")
            return {"tool": "drug_interaction_api", "error": str(e)}
    
    async def _get_rxcui(self, client: httpx.AsyncClient, medication: str) -> Optional[str]:
        """Get RxCUI identifier for medication."""
        try:
            url = f"{self.base_url}/rxcui.json?name={medication}"
            response = await client.get(url)
            data = response.json()
            if data.get("idGroup", {}).get("rxnormId"):
                return data["idGroup"]["rxnormId"][0]
        except:
            pass
        return None
    
    async def _get_interactions(self, client: httpx.AsyncClient, rxcui: str) -> List[Dict]:
        """Get interactions for RxCUI."""
        try:
            url = f"{self.base_url}/interaction/interaction.json?rxcui={rxcui}"
            response = await client.get(url)
            data = response.json()
            interactions = []
            if data.get("interactionTypeGroup"):
                for group in data["interactionTypeGroup"]:
                    for interaction in group.get("interactionType", []):
                        interactions.append({
                            "description": interaction.get("interactionPair", [{}])[0].get("description", ""),
                            "severity": interaction.get("interactionPair", [{}])[0].get("severity", "unknown")
                        })
            return interactions
        except:
            return []


class SymptomCheckerTool:
    """Custom tool for symptom analysis."""
    
    def __init__(self):
        self.logger = configure_logging()
    
    async def analyze_symptoms(self, symptoms: str) -> Dict[str, Any]:
        """Analyze symptoms using rule-based logic."""
        symptom_keywords = {
            "cardiac": ["chest pain", "heart", "palpitations", "shortness of breath"],
            "neurological": ["headache", "dizziness", "vision", "weakness", "numbness"],
            "respiratory": ["cough", "breathing", "wheezing", "chest tightness"],
            "gastrointestinal": ["nausea", "vomiting", "diarrhea", "stomach", "abdominal"]
        }
        
        symptoms_lower = symptoms.lower()
        detected_categories = []
        
        for category, keywords in symptom_keywords.items():
            if any(keyword in symptoms_lower for keyword in keywords):
                detected_categories.append(category)
        
        return {
            "tool": "symptom_checker",
            "input_symptoms": symptoms,
            "detected_categories": detected_categories,
            "primary_category": detected_categories[0] if detected_categories else "general"
        }


class ToolRegistry:
    """Registry for managing custom tools."""
    
    def __init__(self):
        self.tools = {
            "drug_interaction": DrugInteractionTool(),
            "symptom_checker": SymptomCheckerTool()
        }
        self.logger = configure_logging()
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        try:
            tool = self.tools[tool_name]
            if tool_name == "drug_interaction":
                return await tool.check_interactions(kwargs.get("medications", []))
            elif tool_name == "symptom_checker":
                return await tool.analyze_symptoms(kwargs.get("symptoms", ""))
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return {"error": str(e)}
    
    def list_tools(self) -> List[str]:
        """List available tools."""
        return list(self.tools.keys())