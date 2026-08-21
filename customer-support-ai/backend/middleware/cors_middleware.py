"""
CORS Middleware Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Load environment configuration
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "")


def get_cors_headers(request: Request) -> dict:
    """
    Generate safe CORS response headers for custom exception handlers.
    Mirrors the incoming request Origin if present to ensure cross-origin
    error responses (401, 404, 422, 500) pass browser CORS policy without
    triggering invalid wildcard '*' + credentials failures.
    """
    origin = request.headers.get("origin")
    if not origin:
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }


def setup_cors(app: FastAPI) -> None:
    """
    Attach CORS middleware to the FastAPI application.
    Allows requests from configured frontend origins including Render, Vercel, and local environments.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    cors_origins_raw = os.getenv("CORS_ORIGINS", "")

    raw_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://multi-agent-ai-customer-support-ass-eight.vercel.app",
        frontend_url,
    ]

    if cors_origins_raw:
        for org in cors_origins_raw.split(","):
            if org.strip():
                raw_origins.append(org.strip())

    normalized_origins = []
    for org in raw_origins:
        if not org:
            continue
        cleaned = org.strip().rstrip("/")
        if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
            cleaned = f"https://{cleaned}"
        normalized_origins.append(cleaned)
        # Also include without https if local
        if "localhost" in cleaned or "127.0.0.1" in cleaned:
            normalized_origins.append(cleaned.replace("https://", "http://"))

    unique_origins = list(dict.fromkeys(filter(None, normalized_origins)))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=unique_origins,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )


