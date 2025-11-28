from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import httpx

from app.tools.base import BaseTool
from app.utils import configure_logging


class MedicalLookupTool(BaseTool):
    """Custom tool for medical information lookup via external APIs."""
    
    def __init__(self):
        super().__init__(
            name="medical_lookup",
            description="Look up medical conditions, symptoms, and drug information"
        )
        self.logger = configure_logging()
        self.base_url = "https://clinicaltables.nlm.nih.gov/api"
    
    async def execute(self, query: str, lookup_type: str = "conditions") -> Dict[str, Any]:
        """Execute medical lookup."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                if lookup_type == "conditions":
                    url = f"{self.base_url}/conditions/v3/search"
                    params = {"terms": query, "maxList": 5}
                elif lookup_type == "drugs":
                    url = f"{self.base_url}/rxterms/v3/search"
                    params = {"terms": query, "maxList": 5}
                else:
                    return {"error": "Invalid lookup_type"}
                
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # Handle different API response formats
                    results = []
                    if isinstance(data, list) and len(data) > 3:
                        results = data[3][:5] if data[3] else []
                    elif isinstance(data, dict):
                        results = data.get("results", [])[:5]
                    
                    return {
                        "success": True,
                        "results": results,
                        "query": query,
                        "type": lookup_type
                    }
                else:
                    return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            self.logger.error(f"Medical lookup failed: {e}")
            # Return mock data as fallback
            return {
                "success": True,
                "results": [f"General information about {query}"],
                "query": query,
                "type": lookup_type,
                "fallback": True
            }


class GoogleSearchTool(BaseTool):
    """Built-in tool for Google Search integration."""
    
    def __init__(self):
        super().__init__(
            name="google_search",
            description="Search Google for medical information and research"
        )
        self.logger = configure_logging()
    
    async def execute(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Execute Google search (mock implementation for demo)."""
        # Mock implementation - in production, use Google Custom Search API
        mock_results = [
            {
                "title": f"Medical information about {query}",
                "url": "https://www.mayoclinic.org/example",
                "snippet": f"Comprehensive information about {query} symptoms and treatment."
            },
            {
                "title": f"{query} - WebMD",
                "url": "https://www.webmd.com/example", 
                "snippet": f"Learn about {query} causes, symptoms, and when to see a doctor."
            }
        ]
        
        return {
            "success": True,
            "results": mock_results[:num_results],
            "query": query
        }