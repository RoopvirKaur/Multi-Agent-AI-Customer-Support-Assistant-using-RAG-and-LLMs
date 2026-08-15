"""
test_edge_cases_security.py
Edge Cases & Security Checklist Tests (Section 6.4 & 6.6):
- Validation errors for empty / oversized inputs
- Invalid UUID / 404 handling
- 401 Unauthorized on missing / expired JWT
- Multi-tenant cross-user session access isolation
- Git environment secrecy checks
"""

import uuid
import pytest
import httpx
from pathlib import Path
from backend.middleware.auth_middleware import create_access_token
from datetime import timedelta


@pytest.mark.asyncio
async def test_empty_message_validation_error(client: httpx.AsyncClient, token_a: str):
    """
    Submitting an empty message string should trigger Pydantic validation error (422).
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    resp = await client.post(
        "/api/chat/message",
        json={"session_id": None, "message": ""},
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_oversized_message_validation_error(client: httpx.AsyncClient, token_a: str):
    """
    Submitting a message exceeding max_length (4000 characters) should trigger 422.
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    oversized_message = "A" * 4001
    resp = await client.post(
        "/api/chat/message",
        json={"session_id": None, "message": oversized_message},
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_session_id_not_found(client: httpx.AsyncClient, token_a: str):
    """
    Sending a message referencing a non-existent session UUID should return 404.
    """
    headers = {"Authorization": f"Bearer {token_a}"}
    non_existent_uuid = str(uuid.uuid4())
    resp = await client.post(
        "/api/chat/message",
        json={"session_id": non_existent_uuid, "message": "Hello?"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client: httpx.AsyncClient):
    """
    Requests to protected routes without a JWT token must be rejected with 401.
    """
    resp = await client.post(
        "/api/chat/message",
        json={"session_id": None, "message": "Hello?"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_jwt_rejected(client: httpx.AsyncClient, user_a):
    """
    Expired JWT token must be rejected with 401 Unauthorized.
    """
    # Create token expired 1 hour ago
    expired_token = create_access_token(
        {"sub": str(user_a.id), "email": user_a.email},
        expires_delta=timedelta(minutes=-60),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = await client.get("/api/chat/sessions", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_session_isolation(
    client: httpx.AsyncClient,
    token_a: str,
    token_b: str,
):
    """
    Security check: User B must NOT be able to read or append to User A's session.
    """
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User A creates a session
    resp_a = await client.post(
        "/api/chat/message",
        json={"session_id": None, "message": "Private billing inquiry for Alice."},
        headers=headers_a,
    )
    assert resp_a.status_code == 200
    session_id_a = resp_a.json()["session_id"]

    # 2. User B tries to read User A's conversation history
    resp_b_history = await client.get(
        f"/api/history/{session_id_a}",
        headers=headers_b,
    )
    assert resp_b_history.status_code == 404, "User B should not access User A's history"

    # 3. User B tries to post a message into User A's session
    resp_b_post = await client.post(
        "/api/chat/message",
        json={"session_id": session_id_a, "message": "Malicious intrusion attempt"},
        headers=headers_b,
    )
    assert resp_b_post.status_code == 404, "User B should not post to User A's session"


def test_gitignore_security():
    """
    Verify that `.env` files are strictly excluded in `.gitignore`.
    """
    gitignore_path = Path(__file__).resolve().parent.parent.parent / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file must exist in project root"

    content = gitignore_path.read_text()
    assert ".env" in content, ".gitignore must contain .env"
    assert "vectorstore/faiss_index.bin" in content or "*.bin" in content
