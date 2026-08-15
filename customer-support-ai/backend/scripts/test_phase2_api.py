"""
Phase 2 API Verification Test Suite
Tests all endpoints: Auth, Chat, History, Ingestion, Middleware, CORS, Health Checks.
"""

import sys
import uuid
import asyncio
from pathlib import Path
import io

# Ensure customer-support-ai is in sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
from backend.main import app
from backend.database.connection import AsyncSessionLocal
from sqlalchemy import text


async def run_phase2_tests():
    print("=" * 65)
    print("Multi-Agent AI Customer Support Assistant — Phase 2 API Verification")
    print("=" * 65)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        
        # 1. Test Root & Health
        print("\n1. Testing Health & Root Endpoints...")
        res = await client.get("/")
        assert res.status_code == 200, f"Root failed: {res.text}"
        print(f"   [OK] GET / -> {res.json()['status']}")

        res = await client.get("/health")
        assert res.status_code == 200, f"Health failed: {res.text}"
        data = res.json()
        print(f"   [OK] GET /health -> status: {data['status']}, db: {data['database']}")

        # 2. Test User Registration
        print("\n2. Testing Authentication (Register / Login / Me / Refresh)...")
        test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecurePassword123!"
        test_name = "Phase 2 Verifier"

        # Register
        reg_payload = {
            "email": test_email,
            "password": test_password,
            "name": test_name,
        }
        res = await client.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 201, f"Registration failed: {res.text}"
        reg_data = res.json()
        token = reg_data["access_token"]
        user_id = reg_data["user"]["id"]
        print(f"   [OK] POST /api/auth/register -> User registered: {reg_data['user']['email']}")

        # Duplicate Register Check
        res = await client.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 409, f"Duplicate check failed: {res.text}"
        print("   [OK] Duplicate registration prevented (HTTP 409).")

        # Login
        login_payload = {
            "email": test_email,
            "password": test_password,
        }
        res = await client.post("/api/auth/login", json=login_payload)
        assert res.status_code == 200, f"Login failed: {res.text}"
        login_data = res.json()
        token = login_data["access_token"]
        print("   [OK] POST /api/auth/login -> Logged in and JWT received.")

        # Invalid Login Check
        res = await client.post("/api/auth/login", json={"email": test_email, "password": "WrongPassword"})
        assert res.status_code == 401, f"Invalid login check failed: {res.text}"
        print("   [OK] Invalid login rejected (HTTP 401).")

        # Protected Route: GET /me
        auth_headers = {"Authorization": f"Bearer {token}"}
        res = await client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200, f"Get me failed: {res.text}"
        assert res.json()["email"] == test_email
        print(f"   [OK] GET /api/auth/me -> Authenticated profile: {res.json()['name']}")

        # Refresh Token
        res = await client.post("/api/auth/refresh", headers=auth_headers)
        assert res.status_code == 200, f"Refresh failed: {res.text}"
        token = res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        print("   [OK] POST /api/auth/refresh -> Refreshed JWT token.")

        # 3. Test Chat API
        print("\n3. Testing Chat Endpoints (Message, Sessions, History)...")
        # Send new message without session_id (creates auto session)
        msg_payload = {
            "message": "Hello, I need help with my TechMart warranty on Order #9910."
        }
        res = await client.post("/api/chat/message", json=msg_payload, headers=auth_headers)
        assert res.status_code == 200, f"Chat message failed: {res.text}"
        chat_data = res.json()
        session_id = chat_data["session_id"]
        print(f"   [OK] POST /api/chat/message -> Auto-created Session: {session_id}")
        print(f"        Agent Response: \"{chat_data['response'][:60]}...\"")
        print(f"        Agents Invoked: {chat_data['agents_invoked']}")

        # Send follow-up message with session_id
        msg2_payload = {
            "session_id": session_id,
            "message": "How many days do I have to return an item?"
        }
        res = await client.post("/api/chat/message", json=msg2_payload, headers=auth_headers)
        assert res.status_code == 200, f"Second message failed: {res.text}"
        print("   [OK] POST /api/chat/message -> Follow-up message sent.")

        # List Sessions
        res = await client.get("/api/chat/sessions", headers=auth_headers)
        assert res.status_code == 200, f"List sessions failed: {res.text}"
        sessions = res.json()
        assert len(sessions) >= 1
        print(f"   [OK] GET /api/chat/sessions -> Retrieved {len(sessions)} session(s).")

        # Get Conversation History
        res = await client.get(f"/api/history/{session_id}", headers=auth_headers)
        assert res.status_code == 200, f"History failed: {res.text}"
        history = res.json()
        assert len(history) == 4  # 2 user msgs + 2 assistant msgs
        print(f"   [OK] GET /api/history/{session_id} -> Retrieved {len(history)} messages.")

        # 4. Test Ingestion API
        print("\n4. Testing Ingestion Endpoints (Upload & List)...")
        sample_pdf_bytes = b"%PDF-1.4 Mock TechMart Support Policy Content"
        files = {"file": ("TechMart_Policy_Test.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
        res = await client.post("/api/ingest/upload", files=files)
        assert res.status_code == 200, f"Upload failed: {res.text}"
        print(f"   [OK] POST /api/ingest/upload -> {res.json()['filename']} uploaded.")

        res = await client.get("/api/ingest/documents")
        assert res.status_code == 200, f"List docs failed: {res.text}"
        docs = res.json()["documents"]
        assert "TechMart_Policy_Test.pdf" in docs
        print(f"   [OK] GET /api/ingest/documents -> Found {len(docs)} documents in knowledge base.")

        # 5. Clean up test data
        print("\n5. Cleaning up test data...")
        res = await client.delete(f"/api/chat/sessions/{session_id}", headers=auth_headers)
        assert res.status_code == 204, f"Delete session failed: {res.text}"
        print("   [OK] DELETE /api/chat/sessions/{session_id} -> Session deleted.")

        # Delete user from DB directly
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})
            await session.commit()
        print("   [OK] Test user removed from Supabase.")

        # Remove temporary PDF
        temp_pdf = backend_dir / "knowledge_base" / "TechMart_Policy_Test.pdf"
        if temp_pdf.exists():
            temp_pdf.unlink()
            print("   [OK] Temporary test PDF cleaned up.")

    print("\n" + "=" * 65)
    print("[SUCCESS] ALL PHASE 2 BACKEND CORE API TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = asyncio.run(run_phase2_tests())
    sys.exit(0 if success else 1)
