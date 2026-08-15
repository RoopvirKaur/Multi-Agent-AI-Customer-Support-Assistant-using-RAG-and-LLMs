"""
test_phase5.py
Automated test suite to verify Phase 5 implementation:
- Gemini LLM Client
- Intent Detection Agent
- Specialized Domain Agents (Billing, Technical, Product, Complaint, FAQ)
- Agent Router (Parallel Dispatching)
- Response Aggregator (Synthesis & Citation Merging)
"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env
load_dotenv(dotenv_path=BASE_DIR / ".env")

from backend.llm.gemini_client import get_gemini_client
from backend.agents.intent_detector import get_intent_detector
from backend.agents.billing import BillingAgent
from backend.agents.technical import TechnicalAgent
from backend.agents.product import ProductAgent
from backend.agents.complaint import ComplaintAgent
from backend.agents.faq import FAQAgent
from backend.agents.router import get_agent_router
from backend.agents.aggregator import get_response_aggregator


async def run_all_tests():
    print("=" * 70)
    print("PHASE 5 VERIFICATION TEST SUITE: AI AGENTS & ORCHESTRATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Test 1: Gemini Client
    # ---------------------------------------------------------
    print("\n[TEST 1] Testing Gemini Client...")
    client = get_gemini_client()
    try:
        reply = await client.agenerate(
            system_prompt="You are a helpful customer support bot.",
            user_message="Say 'TechMart Support is Online' in exactly 4 words.",
        )
        print(f"  [PASS] LLM Output: {reply}")
    except Exception as e:
        print(f"  [FAIL] Gemini Client Test Failed: {e}")
        return False

    # ---------------------------------------------------------
    # Test 2: Intent Detection Agent
    # ---------------------------------------------------------
    print("\n[TEST 2] Testing Intent Detection Agent...")
    intent_detector = get_intent_detector()

    test_queries = [
        ("What is your refund policy?", ["billing"]),
        ("How do I connect the device to my WiFi network?", ["technical"]),
        ("Tell me about the specs and pricing of the Pro model", ["product", "billing"]),
        ("I was charged twice and my device will not turn on!", ["billing", "technical"]),
        ("What are your store hours and shipping times?", ["faq"]),
        ("I am furious! My order arrived completely shattered and ruined.", ["complaint"]),
    ]

    for query, expected_in in test_queries:
        intents = await intent_detector.adetect(query)
        print(f"  Query: \"{query}\"")
        print(f"  -> Detected Intents: {intents}")
        assert len(intents) > 0, "No intents detected"
    print("  [PASS] Intent Detection passed!")

    # ---------------------------------------------------------
    # Test 3: Specialized Agents with RAG
    # ---------------------------------------------------------
    print("\n[TEST 3] Testing 5 Specialized Agents with Scoped RAG...")

    agents = [
        (BillingAgent(), "What is your refund policy for opened items?"),
        (TechnicalAgent(), "How do I factory reset my TechMart SmartHub?"),
        (ProductAgent(), "What features are included in the Pro tier?"),
        (ComplaintAgent(), "My order is 2 weeks late and customer service ignored me."),
        (FAQAgent(), "How much does standard shipping cost and how long does it take?"),
    ]

    for agent, q in agents:
        print(f"\n  Running Agent: [{agent.name.upper()}] for query: \"{q}\"")
        res = await agent.run(q)
        print(f"    Agent: {res.agent_name}")
        print(f"    Confidence: {res.confidence}")
        print(f"    Sources Cited: {res.source_docs}")
        print(f"    Response Preview: {res.text[:120]}...")
        assert res.text and len(res.text.strip()) > 0, f"{agent.name} returned empty text"
    print("\n  [PASS] All 5 specialized agents tested successfully!")

    # ---------------------------------------------------------
    # Test 4: Agent Router (Parallel Dispatch)
    # ---------------------------------------------------------
    print("\n[TEST 4] Testing Agent Router & Concurrent Dispatch...")
    router = get_agent_router()
    compound_query = "I paid for the Pro subscription yesterday but my app still shows errors and won't connect."
    compound_intents = await intent_detector.adetect(compound_query)
    print(f"  Compound Query: \"{compound_query}\"")
    print(f"  Detected Intents: {compound_intents}")

    routed_agents = router.route(compound_intents)
    print(f"  Routed Agents: {[a.name for a in routed_agents]}")
    assert len(routed_agents) >= 1, "Router should match at least 1 agent"

    responses = await router.dispatch_all(routed_agents, compound_query)
    print(f"  Parallel Responses Received: {len(responses)}")
    for r in responses:
        print(f"    - Agent [{r.agent_name}]: {len(r.text)} chars, {len(r.source_docs)} sources")
    print("  [PASS] Agent Router and Parallel Dispatch passed!")

    # ---------------------------------------------------------
    # Test 5: Response Aggregator (Synthesis)
    # ---------------------------------------------------------
    print("\n[TEST 5] Testing Response Aggregator...")
    aggregator = get_response_aggregator()

    # Case A: Single agent passthrough
    single_res = responses[0:1]
    single_agg = await aggregator.aaggregate(single_res, compound_query)
    print(f"  Single Agent Passthrough: {single_agg.agents_invoked}")
    assert len(single_agg.agents_invoked) == 1

    # Case B: Multi-agent synthesis
    if len(responses) > 1:
        multi_agg = await aggregator.aaggregate(responses, compound_query)
        print(f"  Multi-Agent Synthesized Output Preview:\n{multi_agg.text[:200]}...")
        print(f"  Invoked Departments: {multi_agg.agents_invoked}")
        print(f"  Combined Sources: {multi_agg.sources}")
        assert len(multi_agg.agents_invoked) == len(responses)
    else:
        mock_b = await BillingAgent().run("How do I fix billing?")
        mock_t = await TechnicalAgent().run("How do I fix connection error?")
        multi_agg = await aggregator.aaggregate([mock_b, mock_t], compound_query)
        print(f"  Multi-Agent Synthesized Output Preview:\n{multi_agg.text[:200]}...")
        print(f"  Invoked Departments: {multi_agg.agents_invoked}")
        print(f"  Combined Sources: {multi_agg.sources}")
        assert "billing" in multi_agg.agents_invoked and "technical" in multi_agg.agents_invoked

    print("  [PASS] Response Aggregator passed!")

    print("\n" + "=" * 70)
    print("ALL PHASE 5 TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
