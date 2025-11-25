import pytest

from app.agents.triage import TriageAgent
from app.schemas import TriageRequest


@pytest.mark.asyncio
async def test_red_flag_override():
    agent = TriageAgent()
    request = TriageRequest(
        user_id="test-user",
        symptoms="I have crushing chest pain and trouble breathing",
    )

    response = await agent.run(request)

    assert response.recommended_action == "go_to_er"
    assert "chest pain" in response.red_flags


@pytest.mark.asyncio
async def test_fallback_response_structure():
    agent = TriageAgent()
    request = TriageRequest(
        user_id="test-user",
        symptoms="I have a mild headache after working late",
    )

    response = await agent.run(request)

    assert response.category
    assert response.urgency
    assert isinstance(response.red_flags, list)

