import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.agents.medication import MedicationSafetyAgent
from app.schemas import MedicationCheckRequest


@pytest.mark.asyncio
async def test_detects_high_risk_combo():
    agent = MedicationSafetyAgent()
    request = MedicationCheckRequest(
        user_id="test",
        medications=["Warfarin", "Aspirin"],
    )

    response = await agent.run(request)

    assert response.risk_level == "high"
    assert response.conflicts
    assert any("aspirin" in conflict.medications for conflict in response.conflicts)


@pytest.mark.asyncio
async def test_duplicate_medication_warning():
    agent = MedicationSafetyAgent()
    request = MedicationCheckRequest(
        user_id="test",
        medications=["ibuprofen", "Ibuprofen"],
    )

    response = await agent.run(request)

    assert response.risk_level == "moderate"
    assert any(
        conflict.reason.startswith("Medication listed multiple times")
        for conflict in response.conflicts
    )


def test_medication_endpoint_persists_result():
    payload = {
        "user_id": "endpoint-user",
        "medications": ["ibuprofen", "aspirin"],
    }

    with TestClient(app) as client:
        resp = client.post("/medications/check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] == "high"
        assert data["conflicts"]

        history = client.get("/users/endpoint-user/medication-checks")
        assert history.status_code == 200
        assert len(history.json()) >= 1

