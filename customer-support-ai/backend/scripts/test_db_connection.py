"""
Database Connection & CRUD Verification Script
Tests connectivity to Supabase PostgreSQL and validates ORM models.
"""

import sys
import uuid
import asyncio
from pathlib import Path

# Add backend parent to sys.path so backend modules can be imported
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from backend.database.connection import AsyncSessionLocal, DATABASE_URL, engine
from backend.database import crud


async def test_database():
    print("=" * 60)
    print("Multi-Agent AI Customer Support — Database Verification")
    print("=" * 60)

    if not DATABASE_URL:
        print("[FAIL] DATABASE_URL is not set in .env")
        print("Please copy .env.example to .env and add your Supabase connection string.")
        return False

    # Mask credentials for display
    masked_url = DATABASE_URL
    if "@" in masked_url:
        prefix, rest = masked_url.split("@", 1)
        masked_url = f"{prefix.split(':')[0]}://****:****@{rest}"
    print(f"Connecting to: {masked_url}")

    if AsyncSessionLocal is None:
        print("[FAIL] AsyncSessionLocal could not be initialized.")
        return False

    # 1. Test basic connectivity
    print("\n1. Testing basic connection (SELECT 1)...")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                print("   [OK] Successfully connected to PostgreSQL!")
            else:
                print(f"   [FAIL] Unexpected response: {val}")
                return False
    except Exception as e:
        print(f"   [FAIL] Connection failed: {e}")
        return False

    # 2. Check if required tables exist
    print("\n2. Checking table existence...")
    required_tables = ["users", "sessions", "messages", "analytics_events"]
    existing_tables = []
    try:
        async with AsyncSessionLocal() as session:
            for table in required_tables:
                res = await session.execute(
                    text(
                        "SELECT EXISTS ("
                        "  SELECT FROM information_schema.tables "
                        "  WHERE table_schema = 'public' AND table_name = :t"
                        ")"
                    ),
                    {"t": table},
                )
                exists = res.scalar()
                if exists:
                    print(f"   [OK] Table '{table}' exists.")
                    existing_tables.append(table)
                else:
                    print(f"   [WARN] Table '{table}' does NOT exist yet. (Please run Phase 1.1 DDL script in Supabase SQL editor)")
    except Exception as e:
        print(f"   [FAIL] Failed to inspect tables: {e}")
        return False

    if len(existing_tables) < 3:
        print("\n[INFO] Tables have not all been created in Supabase yet.")
        print("Please run the SQL schema script in your Supabase SQL Editor.")
        return False

    # 3. Test CRUD operations with a test user
    print("\n3. Testing CRUD operations...")
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    test_user_id = None
    test_session_id = None

    try:
        async with AsyncSessionLocal() as session:
            # Create user
            user = await crud.create_user(
                session,
                email=test_email,
                password_hash="testhash123",
                name="Test Verifier",
            )
            test_user_id = user.id
            print(f"   [OK] Created test user: {user.email} (ID: {user.id})")

            # Create session
            sess = await crud.create_session(
                session,
                user_id=user.id,
                title="Test Session Verification",
            )
            test_session_id = sess.id
            print(f"   [OK] Created test session: {sess.title} (ID: {sess.id})")

            # Save message
            msg = await crud.save_message(
                session,
                session_id=sess.id,
                role="user",
                content="Hello, this is a test message!",
                agent_name=None,
                intent=["faq"],
            )
            print(f"   [OK] Saved message: '{msg.content}' (Role: {msg.role})")

            # Retrieve messages
            messages = await crud.get_messages_by_session(session, sess.id)
            print(f"   [OK] Retrieved {len(messages)} message(s) from session.")

            # Cleanup test user (cascades to session and messages)
            await crud.delete_session(session, sess.id, user.id)
            await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user.id})
            await session.commit()
            print("   [OK] Cleaned up test data.")

    except Exception as e:
        print(f"   [FAIL] CRUD operation test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All Phase 1 Database & ORM tests PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
