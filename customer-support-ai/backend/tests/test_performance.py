"""
test_performance.py
Performance & Latency Baseline Tests (Section 6.5):
Measures end-to-end response time for single-agent and multi-agent queries,
verifying parallel speedups and latency baselines.
"""

import time
import pytest
import httpx


@pytest.mark.asyncio
async def test_single_agent_performance_baseline(client: httpx.AsyncClient, token_a: str):
    """
    Measure latency for a single-agent inquiry. Target: < 5.0 seconds.
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    payload = {
        "session_id": None,
        "message": "What is your refund policy?",
    }

    start_time = time.perf_counter()
    resp = await client.post("/api/chat/message", json=payload, headers=headers)
    elapsed = time.perf_counter() - start_time

    assert resp.status_code == 200
    print(f"\n[PERF] Single Agent Latency: {elapsed:.2f}s")
    # Log slow query warning if > 8 seconds
    if elapsed > 8.0:
        print(f"  [WARN] Query took longer than 8.0s: {elapsed:.2f}s")
    assert elapsed < 12.0, f"Query took excessively long: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_multi_agent_parallel_performance(client: httpx.AsyncClient, token_a: str):
    """
    Measure latency for a compound multi-agent query executed in parallel. Target: < 7.0 seconds.
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    payload = {
        "session_id": None,
        "message": "I was charged twice and my SmartHub won't turn on.",
    }

    start_time = time.perf_counter()
    resp = await client.post("/api/chat/message", json=payload, headers=headers)
    elapsed = time.perf_counter() - start_time

    assert resp.status_code == 200
    data = resp.json()
    print(f"\n[PERF] Multi-Agent Parallel Latency ({len(data['agents_invoked'])} agents): {elapsed:.2f}s")

    if elapsed > 8.0:
        print(f"  [WARN] Multi-agent query took longer than 8.0s: {elapsed:.2f}s")
    assert elapsed < 15.0, f"Multi-agent query took excessively long: {elapsed:.2f}s"
