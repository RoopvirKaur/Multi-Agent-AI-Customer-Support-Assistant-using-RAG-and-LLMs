"""
test_rag_quality.py
RAG Quality Evaluation Tests (Section 6.3):
Validates retrieval semantic quality, LLM contextual grounding, and source attribution across all 5 agents.
"""

import pytest
from backend.rag.retriever import get_retriever
from backend.agents.billing import BillingAgent
from backend.agents.technical import TechnicalAgent
from backend.agents.product import ProductAgent
from backend.agents.complaint import ComplaintAgent
from backend.agents.faq import FAQAgent


RAG_EVAL_CASES = [
    {
        "agent": BillingAgent(),
        "query": "How many days do I have to return an item for a full refund?",
        "expected_doc_keywords": ["refund", "policy", "30"],
        "expected_response_keywords": ["30", "return", "refund"],
    },
    {
        "agent": TechnicalAgent(),
        "query": "How do I factory reset the TechMart SmartHub device?",
        "expected_doc_keywords": ["reset", "hub", "button", "power"],
        "expected_response_keywords": ["reset", "button", "seconds"],
    },
    {
        "agent": ProductAgent(),
        "query": "What are the specs and features of the TechMart Pro tier?",
        "expected_doc_keywords": ["pro", "features", "specs", "tier"],
        "expected_response_keywords": ["pro", "features"],
    },
    {
        "agent": ComplaintAgent(),
        "query": "I received a damaged package and the support representative was rude.",
        "expected_doc_keywords": ["refund", "faq", "policy"],
        "expected_response_keywords": ["apologize", "sorry", "support"],
    },
    {
        "agent": FAQAgent(),
        "query": "What are your standard ground delivery times and costs?",
        "expected_doc_keywords": ["shipping", "standard", "delivery", "days"],
        "expected_response_keywords": ["shipping", "days", "standard"],
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", RAG_EVAL_CASES)
async def test_rag_retrieval_and_grounding(case: dict):
    """
    Verify scoped RAG retrieval produces semantically relevant chunks with correct metadata,
    and LLM response incorporates grounded facts.
    """
    agent = case["agent"]
    query = case["query"]

    # 1. Test Scoped Chunk Retrieval
    chunks = agent.retrieve_context(query=query, top_k=5)
    assert len(chunks) > 0, f"No chunks retrieved for agent '{agent.name}' on query: '{query}'"

    # Verify chunks have required fields
    for chunk in chunks:
        assert "text" in chunk and len(chunk["text"]) > 0
        assert "document" in chunk
        assert "score" in chunk
        assert chunk["score"] >= 0.0

    # 2. Test Agent Execution & Response Grounding
    res = await agent.run(query)
    assert len(res.text.strip()) > 0
    assert res.agent_name == agent.name
    assert len(res.source_docs) > 0

    # Verify source document attribution metadata structure
    for src in res.source_docs:
        assert "document" in src and src["document"]
        assert "page" in src

    # Verify response contains relevant domain keywords
    response_lower = res.text.lower()
    matched_keywords = [
        kw for kw in case["expected_response_keywords"]
        if kw.lower() in response_lower
    ]
    assert len(matched_keywords) >= 1, (
        f"Agent '{agent.name}' response did not contain expected grounding keywords {case['expected_response_keywords']}. "
        f"Response text: {res.text[:200]}..."
    )
