"""
FastAPI Application Entry Point
Multi-Agent AI Customer Support Assistant Backend
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

# Load environment configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from backend.database.connection import engine, AsyncSessionLocal
from backend.middleware.cors_middleware import setup_cors
from backend.api import auth_router, chat_router, history_router, ingest_router

# Rate limiter setup: 30 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager:
    - Tests database connectivity on startup
    - Closes connection pools on shutdown
    """
    print("\n" + "=" * 60)
    print("🚀 Starting Multi-Agent AI Customer Support API...")
    print("=" * 60)

    # Test database connectivity
    if AsyncSessionLocal:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print("✅ Database connection verified successfully.")
        except Exception as e:
            print(f"⚠️ Warning: Database connection check failed on startup: {e}")
    else:
        print("⚠️ Warning: Database session factory is not initialized.")

    yield

    # Shutdown
    print("\n🛑 Shutting down Multi-Agent AI Customer Support API...")
    if engine:
        await engine.dispose()
        print("✅ Database engine disposed.")


# Initialize FastAPI application
app = FastAPI(
    title="Multi-Agent AI Customer Support Assistant",
    description=(
        "Production-ready multi-agent customer support backend powered by "
        "Google Gemini, FastAPI, SQLAlchemy, and FAISS vector retrieval."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
setup_cors(app)

# Register API Routers under /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "Multi-Agent AI Customer Support Assistant API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to probe API and database operational status."""
    db_status = "unavailable"
    if AsyncSessionLocal:
        try:
            async with AsyncSessionLocal() as session:
                res = await session.execute(text("SELECT 1"))
                if res.scalar() == 1:
                    db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
