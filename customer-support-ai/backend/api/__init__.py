"""
API package routers.
"""

from backend.api.auth import router as auth_router
from backend.api.chat import router as chat_router
from backend.api.history import router as history_router
from backend.api.ingest import router as ingest_router

__all__ = [
    "auth_router",
    "chat_router",
    "history_router",
    "ingest_router",
]
