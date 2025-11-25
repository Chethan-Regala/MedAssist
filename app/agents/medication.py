from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.schemas import (
    MedicationCheckRequest,
    MedicationCheckResponse,
    MedicationConflict,
)
from app.utils import configure_logging


class MedicationSafetyAgent:
    """Rule-based medication interaction checker with expandable knowledge base."""

    INTERACTION_RULES: Dict[frozenset[str], Dict[str, str]] = {
        frozenset({"ibuprofen", "aspirin"}): {
            "severity": "high",
            "reason": "Dual NSAID therapy increases bleeding and GI ulcer risk.",
        },
        frozenset({"warfarin", "aspirin"}): {
            "severity": "high",
            "reason": "Both thin blood; combination raises hemorrhage risk.",
        },
        frozenset({"metformin", "contrast dye"}): {
            "severity": "moderate",
            "reason": "Contrast agents can precipitate lactic acidosis with metformin.",
        },
        frozenset({"lisinopril", "spironolactone"}): {
            "severity": "moderate",
            "reason": "Dual RAAS blockade can cause hyperkalemia.",
        },
        frozenset({"grapefruit juice", "atorvastatin"}): {
            "severity": "moderate",
            "reason": "Grapefruit inhibits metabolism, raising statin levels.",
        },
    }

    def __init__(self) -> None:
        self.logger = configure_logging()

    async def run(self, request: MedicationCheckRequest) -> MedicationCheckResponse:
        normalized = [med.strip().lower() for med in request.medications if med.strip()]
        conflicts: List[MedicationConflict] = []
        highest_severity = "low"

        severity_rank = {"low": 0, "moderate": 1, "high": 2}

        counts = defaultdict(int)
        for med in normalized:
            counts[med] += 1

        # Duplicate med check (double-dosing same drug)
        for med, count in counts.items():
            if count > 1:
                conflicts.append(
                    MedicationConflict(
                        medications=[med],
                        severity="moderate",
                        reason="Medication listed multiple times; verify dosing frequency.",
                    )
                )
                highest_severity = "moderate"

        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                combo = frozenset({normalized[i], normalized[j]})
                if combo in self.INTERACTION_RULES:
                    rule = self.INTERACTION_RULES[combo]
                    conflicts.append(
                        MedicationConflict(
                            medications=list(combo),
                            severity=rule["severity"],
                            reason=rule["reason"],
                        )
                    )
                    if severity_rank[rule["severity"]] > severity_rank[highest_severity]:
                        highest_severity = rule["severity"]

        if highest_severity == "low":
            guidance = "No known critical conflicts based on the current rule set."
        elif highest_severity == "moderate":
            guidance = "Potential interactions detected; consult primary care before combining."
        else:
            guidance = "High-risk combination detected; seek medical guidance immediately."

        return MedicationCheckResponse(
            risk_level=highest_severity,
            conflicts=conflicts,
            guidance=guidance,
        )

