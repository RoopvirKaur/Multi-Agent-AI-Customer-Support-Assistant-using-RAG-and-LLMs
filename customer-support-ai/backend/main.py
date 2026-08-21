"""
FastAPI Application Entry Point
Multi-Agent AI Customer Support Assistant Backend
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from slowapi import Limiter, _rate_limit_exceeded_handler
# pyrefly: ignore [missing-import]
from slowapi.util import get_remote_address
# pyrefly: ignore [missing-import]
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

# Load environment configuration
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import time
import uuid
from backend.utils.logger import get_logger, setup_root_logging
from backend.database.connection import engine, AsyncSessionLocal
from backend.middleware.cors_middleware import setup_cors, get_cors_headers
from backend.api import auth_router, chat_router, history_router, ingest_router

# Initialize structured logging
setup_root_logging()
logger = get_logger("fastapi_app")

# Rate limiter setup: 30 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager:
    - Tests database connectivity and creates tables if they don't exist
    - Closes connection pools on shutdown
    """
    logger.info("🚀 Starting Multi-Agent AI Customer Support API...")

    # Test database connectivity and auto-create schema tables
    if engine:
        try:
            from backend.database.connection import Base
            import backend.database.models  # noqa: F401
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database connection verified & schema tables initialized.")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Database connection / table initialization check: {e}")
    else:
        logger.warning("⚠️ Warning: Database engine is not initialized.")

    # Pre-warm Embedding Model and FAISS Vector Store
    try:
        from backend.rag.retriever import get_retriever
        retriever = get_retriever()
        retriever.ensure_index_loaded()
        logger.info("✅ FAISS vectorstore loaded & ready.")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not pre-load vectorstore: {e}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Multi-Agent AI Customer Support API...")
    if engine:
        await engine.dispose()
        logger.info("✅ Database engine disposed.")


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

# Configure CORS as primary outermost middleware BEFORE logging / HTTP middleware
setup_cors(app)

# HTTP Request Logging & Timing Middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000
    status_code = response.status_code

    # Structured request log
    logger.info(
        f"{request.method} {request.url.path} -> {status_code} | "
        f"{duration_ms:.2f}ms | client={client_host} | req_id={req_id}"
    )
    return response

# Configure Rate Limiting
app.state.limiter = limiter


from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Rate limit exceeded. {exc.detail}"},
        headers=headers,
    )


# Global Exception Handler (Ensures CORS headers and clean JSON on unexpected errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"❌ Unhandled Exception on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Backend Error: {str(exc)}",
            "path": request.url.path,
        },
        headers=get_cors_headers(request),
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    headers = get_cors_headers(request)
    if exc.headers:
        headers.update(exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )



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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
