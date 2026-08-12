"""
CORS Middleware Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment configuration
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def setup_cors(app: FastAPI) -> None:
    """
    Attach CORS middleware to the FastAPI application.
    Allows requests from configured frontend origins.
    """
    origins = [
        FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Filter out empty or duplicate origins
    unique_origins = list(dict.fromkeys(filter(None, origins)))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=unique_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
