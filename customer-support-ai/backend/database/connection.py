"""
Database Connection & Session Factory
Uses SQLAlchemy AsyncEngine with asyncpg driver for PostgreSQL (Supabase).
"""

import os
from pathlib import Path
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# Load .env file from the customer-support-ai root directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Normalize URL for SQLAlchemy + asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Strip any sslmode query params which asyncpg doesn't accept directly in the URL query string
if "?" in DATABASE_URL:
    base_url, query_params = DATABASE_URL.split("?", 1)
    # Filter out sslmode param if present
    params = [p for p in query_params.split("&") if not p.startswith("sslmode=")]
    DATABASE_URL = base_url + ("?" + "&".join(params) if params else "")

# Base declarative class for ORM models
class Base(DeclarativeBase):
    pass

# Create Async Engine
engine = None
AsyncSessionLocal = None

import ssl

# Configure SSL context for Supabase PostgreSQL
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

if DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,      # Automatically reconnect on dropped connections
        pool_size=10,            # Sensible default pool size for FastAPI
        max_overflow=20,
        connect_args={
            "ssl": ssl_ctx
        } if ("supabase.co" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL) else {}
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session per request.
    Ensures session is properly closed after request completes.
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not set or engine could not be initialized. "
            "Please configure your DATABASE_URL in .env."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
