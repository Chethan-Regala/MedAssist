from __future__ import annotations

from typing import Any, Dict, List

from app.agents.triage import TriageAgent
from app.schemas import TriageRequest, TriageResponse
from app.utils import configure_logging


class AgentEvaluator:
    """Systematic evaluation framework for agent performance."""
    
    def __init__(self):
        self.logger = configure_logging()
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load evaluation test cases."""
        return [
            {
                "input": {"user_id": "eval-1", "symptoms": "severe chest pain and shortness of breath"},
                "expected": {"urgency": "high", "recommended_action": "go_to_er"},
                "category": "emergency"
            },
            {
                "input": {"user_id": "eval-2", "symptoms": "mild headache after long day"},
                "expected": {"urgency": "low", "recommended_action": "self_care"},
                "category": "routine"
            },
            {
                "input": {"user_id": "eval-3", "symptoms": "persistent cough for 2 weeks"},
                "expected": {"urgency": "moderate", "recommended_action": "primary_care"},
                "category": "moderate"
            }
        ]
    
    async def evaluate_triage_agent(self, agent: TriageAgent) -> Dict[str, Any]:
        """Evaluate triage agent performance."""
        results = []
        correct_predictions = 0
        
        for case in self.test_cases:
            request = TriageRequest(**case["input"])
            response = await agent.run(request)
            
            # Check correctness
            is_correct = self._check_prediction(response, case["expected"])
            if is_correct:
                correct_predictions += 1
            
            results.append({
                "case": case["category"],
                "input": case["input"]["symptoms"],
                "expected": case["expected"],
                "actual": {
                    "urgency": response.urgency,
                    "recommended_action": response.recommended_action,
                    "category": response.category
                },
                "correct": is_correct
            })
        
        accuracy = correct_predictions / len(self.test_cases)
        
        return {
            "accuracy": accuracy,
            "total_cases": len(self.test_cases),
            "correct_predictions": correct_predictions,
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _check_prediction(self, response: TriageResponse, expected: Dict[str, Any]) -> bool:
        """Check if prediction matches expected outcome."""
        urgency_match = response.urgency == expected.get("urgency")
        action_match = response.recommended_action == expected.get("recommended_action")
        return urgency_match and action_match
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate evaluation summary."""
        by_category = {}
        for result in results:
            category = result["case"]
            if category not in by_category:
                by_category[category] = {"total": 0, "correct": 0}
            by_category[category]["total"] += 1
            if result["correct"]:
                by_category[category]["correct"] += 1
        
        # Calculate accuracy by category
        for category in by_category:
            total = by_category[category]["total"]
            correct = by_category[category]["correct"]
            by_category[category]["accuracy"] = correct / total if total > 0 else 0
        
        return {
            "by_category": by_category,
            "strengths": [cat for cat, data in by_category.items() if data["accuracy"] >= 0.8],
            "weaknesses": [cat for cat, data in by_category.items() if data["accuracy"] < 0.6]
        }