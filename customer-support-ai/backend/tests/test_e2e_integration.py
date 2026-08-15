"""
test_e2e_integration.py
End-to-End Integration Tests (Section 6.1):
1. Auth flow: Register -> Login -> Get JWT -> Access protected routes
2. New session creation: Message without session_id auto-creates thread
3. Conversation memory: Multi-turn conversation retains context across messages
4. History retrieval: Sessions listing and full session history retrieval
"""

import uuid
import pytest
import httpx


@pytest.mark.asyncio
async def test_auth_flow_e2e(client: httpx.AsyncClient):
    """
    Test complete authentication flow: Register -> Login -> Verify JWT on protected route.
    """
    unique_email = f"test_e2e_{uuid.uuid4().hex[:8]}@techmart.com"
    password = "SecurePassword123!"

    # 1. Register
    reg_resp = await client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": password, "name": "E2E Tester"},
    )
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_email

    # 2. Login
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": password},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    token = login_data["access_token"]
    assert token

    # 3. Access Protected Route (/api/auth/me)
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email


@pytest.mark.asyncio
async def test_session_auto_creation_and_messaging(client: httpx.AsyncClient, token_a: str):
    """
    Test sending a message without session_id auto-creates a session and returns AI response.
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    payload = {
        "session_id": None,
        "message": "What is the warranty period for TechMart electronics?",
    }

    resp = await client.post("/api/chat/message", json=payload, headers=headers)
    assert resp.status_code == 200, f"Message send failed: {resp.text}"
    data = resp.json()

    assert data["session_id"] is not None
    assert data["message_id"] is not None
    assert len(data["response"]) > 0
    assert "faq" in data["agents_invoked"] or "technical" in data["agents_invoked"]
    assert len(data["sources"]) > 0

    session_id = data["session_id"]

    # Verify session appears in session list
    sessions_resp = await client.get("/api/chat/sessions", headers=headers)
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    matching = [s for s in sessions if s["id"] == session_id]
    assert len(matching) == 1
    assert matching[0]["title"] is not None


@pytest.mark.asyncio
async def test_multi_turn_conversation_memory(client: httpx.AsyncClient, token_a: str):
    """
    Test multi-turn conversation memory across multiple messages in the same session.
    """
    headers = {"Authorization": f"Bearer {token_a}"}

    # Turn 1: Inquire about Pro subscription pricing
    t1_payload = {
        "session_id": None,
        "message": "How much does the Pro subscription cost per month?",
    }
    t1_resp = await client.post("/api/chat/message", json=t1_payload, headers=headers)
    assert t1_resp.status_code == 200
    t1_data = t1_resp.json()
    session_id = t1_data["session_id"]

    # Turn 2: Follow-up referencing earlier topic
    t2_payload = {
        "session_id": session_id,
        "message": "Are there any discounts if I pay annually instead of monthly?",
    }
    t2_resp = await client.post("/api/chat/message", json=t2_payload, headers=headers)
    assert t2_resp.status_code == 200
    t2_data = t2_resp.json()
    assert t2_data["session_id"] == session_id
    assert len(t2_data["response"]) > 0

    # Turn 3: Verify history endpoint contains all user and assistant turns in order
    hist_resp = await client.get(f"/api/history/{session_id}", headers=headers)
    assert hist_resp.status_code == 200
    messages = hist_resp.json()
    assert len(messages) >= 4  # 2 user messages + 2 assistant replies

    # Chronological turn order verification
    roles = [m["role"] for m in messages[-4:]]
    assert roles == ["user", "assistant", "user", "assistant"]
