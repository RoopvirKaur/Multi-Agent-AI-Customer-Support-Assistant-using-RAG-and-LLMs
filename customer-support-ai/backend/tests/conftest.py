"""
conftest.py
Pytest fixtures for Multi-Agent AI Support Assistant integration tests.
Uses SQLAlchemy NullPool to eliminate asyncpg cross-loop connection conflicts.
"""

import sys
import os
import ssl
import uuid
import pytest
# pyrefly: ignore [missing-import]
import pytest_asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(dotenv_path=BASE_DIR / ".env")

import httpx
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.main import app
from backend.database.connection import DATABASE_URL, get_db
from backend.database import crud
from backend.database.models import User
from backend.middleware.auth_middleware import (
    create_access_token,
    get_password_hash,
)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Create test engine with NullPool
test_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={"ssl": ssl_ctx} if ("supabase.co" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL) else {},
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
async def user_a():
    """Create or retrieve test User A."""
    async with TestAsyncSessionLocal() as db:
        email = "user_a_test@techmart.com"
        user = await crud.get_user_by_email(db, email=email)
        if not user:
            user = await crud.create_user(
                db=db,
                email=email,
                password_hash=get_password_hash("Password123!"),
                name="Alice Test",
            )
        return user


@pytest_asyncio.fixture(scope="session")
async def user_b():
    """Create or retrieve test User B (for cross-user authorization tests)."""
    async with TestAsyncSessionLocal() as db:
        email = "user_b_test@techmart.com"
        user = await crud.get_user_by_email(db, email=email)
        if not user:
            user = await crud.create_user(
                db=db,
                email=email,
                password_hash=get_password_hash("Password123!"),
                name="Bob Test",
            )
        return user


@pytest_asyncio.fixture(scope="session")
def token_a(user_a):
    """JWT token for User A."""
    return create_access_token({"sub": str(user_a.id), "email": user_a.email})


@pytest_asyncio.fixture(scope="session")
def token_b(user_b):
    """JWT token for User B."""
    return create_access_token({"sub": str(user_b.id), "email": user_b.email})


@pytest_asyncio.fixture
async def client():
    """Async HTTP client connected directly to the FastAPI ASGI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
