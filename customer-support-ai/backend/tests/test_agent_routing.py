"""
test_agent_routing.py
Agent Routing & Intent Dispatch Tests (Section 6.2):
Validates intent classification and agent selection across the 7 canonical test queries.
"""

import pytest
from backend.agents.intent_detector import get_intent_detector
from backend.agents.router import get_agent_router


ROUTING_TEST_CASES = [
    {
        "query": "Can I get a refund?",
        "expected_intents": ["billing"],
        "expected_agents": ["billing"],
    },
    {
        "query": "I can't install the app on my phone.",
        "expected_intents": ["technical"],
        "expected_agents": ["technical"],
    },
    {
        "query": "What's included in the Pro plan?",
        "expected_intents": ["product"],
        "expected_agents": ["product"],
    },
    {
        "query": "I'm very unhappy with your service, nobody answered my emails!",
        "expected_intents": ["complaint"],
        "expected_agents": ["complaint"],
    },
    {
        "query": "What are your business hours?",
        "expected_intents": ["faq"],
        "expected_agents": ["faq"],
    },
    {
        "query": "I paid for the subscription but Premium features are still locked and inaccessible.",
        "expected_intents": ["billing", "technical"],
        "expected_agents": ["billing", "technical"],
    },
    {
        "query": "The product broke immediately after delivery, I am very upset and want a full refund!",
        "expected_intents": ["billing", "complaint"],
        "expected_agents": ["billing", "complaint"],
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ROUTING_TEST_CASES)
async def test_canonical_agent_routing(case: dict):
    """
    Verify intent detector accurately identifies domain intents and router resolves expected agents.
    """
    intent_detector = get_intent_detector()
    router = get_agent_router()

    query = case["query"]
    detected = await intent_detector.adetect(query)
    routed_agents = router.route(detected)
    agent_names = [a.name for a in routed_agents]

    # Verify each expected intent/agent is present
    for exp_agent in case["expected_agents"]:
        assert exp_agent in agent_names, (
            f"Query '{query}' expected agent '{exp_agent}' in {agent_names} "
            f"(Detected intents: {detected})"
        )
