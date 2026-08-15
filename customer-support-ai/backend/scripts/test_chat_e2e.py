"""
test_chat_e2e.py
End-to-end test for FastAPI /api/chat/message with live Multi-Agent Orchestration.
"""

import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(dotenv_path=BASE_DIR / ".env")

import httpx
from backend.main import app
from backend.database.connection import get_db, AsyncSessionLocal
from backend.database import crud
from backend.database.models import User
from backend.middleware.auth_middleware import create_access_token


async def test_endpoint():
    print("Testing /api/chat/message endpoint end-to-end...")

    # 1. Create or get test user
    async with AsyncSessionLocal() as db:
        test_email = "test_agent_user@techmart.com"
        user = await crud.get_user_by_email(db, test_email)
        if not user:
            user = await crud.create_user(
                db=db,
                email=test_email,
                password_hash="fakehashforpytest",
                name="Test Agent User",
            )
        user_id = str(user.id)

    # 2. Generate test JWT
    token = create_access_token({"sub": user_id, "email": test_email})

    # 3. Call endpoint via AsyncClient
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Query 1: Compound Multi-intent inquiry
        payload = {
            "session_id": None,
            "message": "I was charged twice on my invoice and my SmartHub device will not turn on.",
        }
        resp = await client.post("/api/chat/message", json=payload, headers=headers)
        print(f"Status code: {resp.status_code}")
        assert resp.status_code == 200, f"Error: {resp.text}"

        data = resp.json()
        print("\nAPI Response payload (Turn 1):")
        print(f"  Session ID: {data['session_id']}")
        print(f"  Message ID: {data['message_id']}")
        print(f"  Agents Invoked: {data['agents_invoked']}")
        print(f"  Detected Intent: {data['intent']}")
        print(f"  Sources Cited: {data['sources']}")
        print(f"  Response Preview:\n{data['response'][:250]}...\n")

        assert len(data["agents_invoked"]) >= 1
        assert len(data["sources"]) > 0
        assert len(data["response"]) > 20
        session_id = data["session_id"]

        # Test Query 2: Follow-up in same session
        payload2 = {
            "session_id": session_id,
            "message": "What is the return window if I need to send it back?",
        }
        resp2 = await client.post("/api/chat/message", json=payload2, headers=headers)
        assert resp2.status_code == 200, f"Error: {resp2.text}"
        data2 = resp2.json()
        print("\nAPI Response payload (Turn 2 - Follow-up):")
        print(f"  Session ID: {data2['session_id']}")
        print(f"  Agents Invoked: {data2['agents_invoked']}")
        print(f"  Sources Cited: {data2['sources']}")
        print(f"  Response Preview:\n{data2['response'][:250]}...\n")

        assert data2["session_id"] == session_id
        assert "billing" in data2["agents_invoked"] or "faq" in data2["agents_invoked"]

        print("[PASS] End-to-end /api/chat/message API multi-turn tests passed!")


if __name__ == "__main__":
    asyncio.run(test_endpoint())
